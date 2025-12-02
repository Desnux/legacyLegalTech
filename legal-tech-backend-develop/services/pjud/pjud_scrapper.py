import logging
import re
import unicodedata
import os
import aiohttp
import traceback
from datetime import datetime, date
from typing import Optional
from urllib.parse import urlparse

from playwright.async_api import async_playwright, Page, Locator, TimeoutError
from sqlmodel import Session, select

from models.pydantic import CaseNotebookRequest, CaseNotebookResponse, CaseNotebookItem
from models.sql.pjud_folio import PJUDFolio
from models.sql.tribunal import Tribunal
from models.sql.suggestion import CaseEventSuggestion
from models.sql.case import Case, CaseEvent, CaseEventType, CaseParty
from uuid import uuid4
from database.ext_db import get_session
from services.v2.document.demand_exception.event_manager import DemandExceptionEventManager
from services.v2.document.dispatch_resolution.event_manager import DispatchResolutionEventManager

hitos_4 = [
            "búsqueda negativa",
            "búsqueda positiva", 
            "notificación de demanda",
            "notificación exitosa"
]

# Hitos que no necesitan descargar PDF (solo crear evento)
HITOS_SIN_PDF = ["hito4", "hito6", "hito7a", "hito7b"]


def parse_procedure_date(date_str: str) -> Optional[date]:
    if not date_str or not isinstance(date_str, str):
        return None
    
    try:
        cleaned_date = date_str.strip()
        
        if '(' in cleaned_date:
            cleaned_date = cleaned_date.split('(')[0].strip()
        
        day, month, year = cleaned_date.split('/')
        
        return date(int(year), int(month), int(day))
        
    except (ValueError, AttributeError, IndexError) as e:
        logging.warning(f"Failed to parse date '{date_str}': {e}")
        return None


PJUD_URL = "https://oficinajudicialvirtual.pjud.cl/home/index.php"
DEFAULT_WAIT_FOR_TIMEOUT = 3000

FOLIO_COLUMN_INDEX = 0
DOC_COLUMN_INDEX = 1
STAGE_COLUMN_INDEX = 3
PROCEDURE_COLUMN_INDEX = 4
DESC_TRAMITE_INDEX = 5
DATE_COLUMN_INDEX = 6
PAGE_COLUMN_INDEX = 7

MIN_REQUIRED_COLUMNS = 7

LOG_LEVEL_INFO = logging.INFO
LOG_LEVEL_WARNING = logging.WARNING
LOG_LEVEL_ERROR = logging.ERROR
LOG_LEVEL_DEBUG = logging.DEBUG


class PJUDScrapper:
    """Scrapper for extracting case notebook information from PJUD"""
    
    def __init__(self, headless: bool = True):
        self.headless = headless

    async def click_by_text(self, page: Page, text_regex: str, role: str = "link|button") -> bool:
        """Click element by text content using regex"""
        for r in role.split("|"):
            try:
                await page.get_by_role(r, name=re.compile(text_regex, re.I)).first.click(timeout=1000)
                return True
            except Exception:
                pass
        try:
            await page.locator(f'a:has-text("{text_regex}")').first.click(timeout=1000)
            return True
        except Exception:
            return False

    async def click_fast(self, page: Page, text_regex: str, role: str = "link|button") -> bool:
        """Fast version for main clicks"""
        for r in role.split("|"):
            try:
                await page.get_by_role(r, name=re.compile(text_regex, re.I)).first.click(timeout=500)
                return True
            except Exception:
                pass
        try:
            await page.locator(f'a:has-text("{text_regex}")').first.click(timeout=500)
            return True
        except Exception:
            return False

    async def find_select_by_label(self, page: Page, label_regex: str) -> Optional[Locator]:
        """Find select element by label text with improved robustness"""
        try:
            # Esperar a que la página se estabilice
            await page.wait_for_timeout(500)
            
            # Buscar label con múltiples estrategias
            lbl = page.locator("label", has_text=re.compile(label_regex, re.I)).first
            
            # Esperar a que el label esté visible
            try:
                await lbl.wait_for(state="visible", timeout=3000)
            except:
                logging.warning(f">>> ⚠️ Label '{label_regex}' no se hizo visible en 3 segundos")
            
            if await lbl.count() == 0:
                logging.warning(f">>> ⚠️ No se encontró label con patrón: {label_regex}")
                return None
            
            # Intentar encontrar el select asociado
            for_attr = await lbl.get_attribute("for")
            if for_attr:
                sel = page.locator(f"select#{for_attr}")
                if await sel.count() > 0:
                    logging.info(f">>> ✅ Select encontrado por atributo 'for': {for_attr}")
                    return sel
            
            # Buscar select siguiente al label
            next_sel = lbl.locator("xpath=following::select[1]")
            if await next_sel.count() > 0:
                logging.info(f">>> ✅ Select encontrado como siguiente elemento del label")
                return next_sel
            
            logging.warning(f">>> ⚠️ No se encontró select asociado al label: {label_regex}")
            return None
            
        except Exception as e:
            logging.error(f">>> ❌ Error buscando select por label '{label_regex}': {e}")
            return None

    async def wait_select_ready(self, page: Page, sel: Locator, min_options: int = 2, timeout_ms: int = 5000) -> bool:
        """Wait for select to be ready with minimum options"""
        try:
            await sel.wait_for(state="visible", timeout=timeout_ms)
            
            max_attempts = 3 if timeout_ms <= 2000 else (5 if timeout_ms <= 3000 else 10)
            step_time = 30 if timeout_ms <= 2000 else (50 if timeout_ms <= 3000 else 100)
            
            for _ in range(max_attempts):
                if await sel.count() and not await sel.is_disabled():
                    if await sel.locator("option").count() >= min_options:
                        return True
                await page.wait_for_timeout(step_time)
            return False
        except Exception:
            return False

    async def select_by_label_text(self, page: Page, sel: Locator, patterns: list[str], fast_mode: bool = False) -> None:
        """Select option by matching label text patterns"""
    
        timeout = 2000 if fast_mode else 5000
        await sel.wait_for(state="visible", timeout=timeout)
        opts = sel.locator("option")
        count = await opts.count()
        target_val = None

        texts = [(await opts.nth(i).inner_text() or "").strip() for i in range(count)]
        for pat in patterns:
            for i, txt in enumerate(texts):
                if re.search(pat, txt, re.I):
                    val = await opts.nth(i).get_attribute("value")
                    target_val = val if val else txt
                    break
            if target_val:
                break

        if target_val is None and count > 1:
            for i, txt in enumerate(texts):
                if txt and not re.search(r"(seleccione|--)", txt, re.I):
                    val = await opts.nth(i).get_attribute("value")
                    target_val = val if val else txt
                    break

        if target_val is None:
            logging.info(f">>> Opciones disponibles: {texts}")
            raise RuntimeError("No encontré una opción válida en el select.")

        await sel.select_option(value=target_val)
        await sel.evaluate("el => el.dispatchEvent(new Event('change', {bubbles:true}))")
        wait_time = 100 if fast_mode else 200
        await page.wait_for_timeout(wait_time)
        logging.info(f">>> Seleccionado: {target_val}")

    async def fill_input_fast(self, page: Page, label_regex: str, text: str) -> bool:
        """Fast input filling by label"""
        try:
            await page.get_by_label(re.compile(label_regex, re.I)).fill(str(text))
            return True
        except Exception:
            pass
        try:
            lbl = page.locator("label", has_text=re.compile(label_regex, re.I)).first
            if await lbl.count():
                inp = lbl.locator("xpath=following::input[1]")
                if await inp.count():
                    await inp.fill(str(text))
                    return True
        except Exception:
            pass
        return False

    async def close_modal_if_present(self, page: Page) -> bool:
        """Close modal if present by clicking the 'Cerrar' button"""
        try:
            close_selectors = [
                'button[data-dismiss="modal"]',
                'button:has-text("Cerrar")',
                '.modal .btn:has-text("Cerrar")',
                '.modal-footer button:has-text("Cerrar")',
                'button.btn:has-text("Cerrar")'
            ]
            
            for selector in close_selectors:
                try:
                    close_button = page.locator(selector).first
                    if await close_button.count() > 0 and await close_button.is_visible():
                        await close_button.click(timeout=2000)
                        logging.info(f">>> Modal cerrado usando selector: {selector}")
                        await page.wait_for_timeout(500)
                        return True
                except Exception:
                    continue
            
            modal = page.locator('.modal.in, .modal.show').first
            if await modal.count() > 0 and await modal.is_visible():
                await page.keyboard.press('Escape')
                logging.info(">>> Modal cerrado usando tecla ESC")
                await page.wait_for_timeout(500)
                return True
                
            logging.info(">>> No se encontró modal para cerrar")
            return False
            
        except Exception as e:
            logging.warning(f">>> Error al intentar cerrar modal: {e}")
            return False

    def normalize_text(self, text: str) -> str:
        """Normalize text to handle special characters and accents"""
        if not text:
            return ""
        
        if isinstance(text, bytes):
            try:
                text = text.decode('utf-8')
            except UnicodeDecodeError:
                try:
                    text = text.decode('latin-1')
                except UnicodeDecodeError:
                    text = text.decode('utf-8', errors='ignore')

        text = unicodedata.normalize('NFD', text)
        return text.strip()

    def get_tribunal_name_by_id(self, tribunal_id: str) -> str:
        session = next(get_session())
        try:
            statement = select(Tribunal).where(Tribunal.id == tribunal_id)
            tribunal = session.exec(statement).first()
            
            if not tribunal:
                raise ValueError(f"Tribunal ID {tribunal_id} not found in database")
            
            return tribunal.name
        finally:
            session.close()

    def generate_tribunal_patterns(self, tribunal_name: str) -> list[str]:
        patterns = []

        exact_pattern = re.escape(tribunal_name)
        exact_pattern = exact_pattern.replace(r'\ ', r'\s+')
        exact_pattern = exact_pattern.replace(r'°', r'(\s*°|º)?')
        patterns.append(exact_pattern)
        
        flexible_pattern = re.escape(tribunal_name)
        flexible_pattern = flexible_pattern.replace(r'\ ', r'.*')
        flexible_pattern = flexible_pattern.replace(r'°', r'(\s*°|º)?')
        patterns.append(flexible_pattern)
        
        case_insensitive = f"(?i){re.escape(tribunal_name)}"
        case_insensitive = case_insensitive.replace(r'\ ', r'\s+')
        case_insensitive = case_insensitive.replace(r'°', r'(\s*°|º)?')
        patterns.append(case_insensitive)
        
        return patterns

    def identify_hitos(self, rows_data: list[list[str]], headers: list[str]) -> list[list[str]]:
        """Identify and classify rows according to specific milestones"""
        logging.info(">>> Identificando hitos...")
        
        if DESC_TRAMITE_INDEX >= len(headers):
            logging.error(f">>> Error: El índice {DESC_TRAMITE_INDEX} está fuera del rango de headers (0-{len(headers)-1})")
            return []
        
        rows_data_reversed = rows_data[::-1]
        
        logging.info(">>> Filas invertidas: procesando desde el más reciente al más antiguo")
        
        hitos_data = []
        hito_4_count = 0

        for row in rows_data_reversed:
            if len(row) <= DESC_TRAMITE_INDEX:
                continue
                
            desc_tramite = row[DESC_TRAMITE_INDEX].lower()
            procedure = row[PROCEDURE_COLUMN_INDEX].lower()
            desc_tramite = re.sub(r'\s+', ' ', desc_tramite)

            logging.info(f">>> Analizando texto: '{desc_tramite}'")
            
            hito = None
            
            if "ingreso demanda" in desc_tramite:
                hito = "Hito 2"
                logging.info(f"   >>> BUSCANDO: 'ingreso demanda' - ENCONTRADO: '{desc_tramite}'")
            
            elif "ordena despachar mandamiento" in desc_tramite:
                hito = "Hito 3"
                logging.info(f"   >>> BUSCANDO: 'ordena despachar mandamiento' - ENCONTRADO: '{desc_tramite}'")
            
            elif any(keyword in desc_tramite for keyword in hitos_4):
                hito_4_count += 1
                hito = f"Hito 4.{hito_4_count}"
                logging.info(f"   >>> BUSCANDO: 'notificación/búsqueda/certificación' - ENCONTRADO: '{desc_tramite}'")
            
            elif "opone excepciones" in desc_tramite and "escrito" in procedure:
                hito = "Hito 5"
                logging.info(f"   >>> BUSCANDO: 'opone excepciones' - ENCONTRADO: '{desc_tramite}'")
            
            elif "evacúa traslado" in desc_tramite:
                hito = "Hito 6"
                logging.info(f"   >>> BUSCANDO: 'evacúa traslado' - ENCONTRADO: '{desc_tramite}'")
            
            elif "recibe la causa a prueba" in desc_tramite:
                hito = "Hito 7a"
                logging.info(f"   >>> BUSCANDO: 'recibe la causa a prueba' - ENCONTRADO: '{desc_tramite}'")
            elif "sentencia" in desc_tramite:
                hito = "Hito 7b"
                logging.info(f"   >>> BUSCANDO: 'sentencia' - ENCONTRADO: '{desc_tramite}'")
            
            if hito:
                logging.info(f">>> Hito encontrado: {hito} - Texto: '{desc_tramite}'")
            
            row_with_hito = row.copy()
            row_with_hito.append(hito)
            hitos_data.append(row_with_hito)
        
        return hitos_data

    async def extract_table_data(self, page: Page) -> tuple[list[CaseNotebookItem], list[dict]]:
        """Extract table data from the modal"""
        logging.info(">>> Esperando a que el modal se abra...")
        
        table_selector = "table:has(th:has-text('Folio')):has(th:has-text('Doc.')):has(th:has-text('Etapa'))"
        modal_table = page.locator(table_selector).first
        await modal_table.wait_for(state="visible", timeout=5000)
        
        headers = []
        header_cells = modal_table.locator("thead th")
        header_count = await header_cells.count()
        for i in range(header_count):
            header_text = await header_cells.nth(i).inner_text()
            header_text = self.normalize_text(header_text)
            headers.append(header_text)
        logging.info(f">>> Encabezados encontrados: {headers}")
        
        rows_data = []
        rows = modal_table.locator("tbody tr")
        rows_count = await rows.count()
        for i in range(rows_count):
            row = rows.nth(i)
            cells = row.locator("td")
            row_data = []
            cells_count = await cells.count()
            for j in range(cells_count):
                cell_text = await cells.nth(j).inner_text()
                cell_text = self.normalize_text(cell_text)
                row_data.append(cell_text)
            rows_data.append(row_data)
        
        logging.info(f">>> Total de filas extraídas: {len(rows_data)}")
        
        hitos_data = self.identify_hitos(rows_data, headers)
        
        case_id = getattr(self, '_current_case_id', None)
        case_number = getattr(self, '_current_case_number', None)
        year = getattr(self, '_current_year', None)
        
        logging.info(">>> 📥 INICIANDO PROCESO DE DESCARGA DE PDFs...")
        logging.info(f">>> 🆔 Case ID: {case_id}")
        logging.info(f">>> 📋 Case Number: {case_number}")
        logging.info(f">>> 📅 Year: {year}")
        logging.info(f">>> 📊 Total hitos detectados: {len([row for row in hitos_data if len(row) > DESC_TRAMITE_INDEX and row[-1]])}")
        
        milestone_events = await self.process_milestone_events(page, modal_table, hitos_data, case_id=case_id, case_number=case_number, year=year)
        
        logging.info(f">>> 📥 RESULTADO DE PROCESAMIENTO:")
        logging.info(f">>>    Eventos procesados: {len(milestone_events)}")
        for i, event_info in enumerate(milestone_events, 1):
            pdf_status = "Con PDF" if event_info.get('pdf_path') else "Sin PDF"
            logging.info(f">>>    {i}. {event_info.get('milestone_type', 'unknown')} - {pdf_status}")

        items = []
        for i, row in enumerate(hitos_data):
            if len(row) >= MIN_REQUIRED_COLUMNS:
                try:
                    folio_number = int(row[FOLIO_COLUMN_INDEX]) if row[FOLIO_COLUMN_INDEX] and row[FOLIO_COLUMN_INDEX].isdigit() else 0
                    
                    page = int(row[PAGE_COLUMN_INDEX]) if len(row) > PAGE_COLUMN_INDEX and row[PAGE_COLUMN_INDEX] and row[PAGE_COLUMN_INDEX].isdigit() else None

                    milestone = row[-1] if len(row) > PAGE_COLUMN_INDEX and row[-1] else None
                    if milestone:
                        logging.info(f">>> 📋 HITO DETECTADO: {milestone} - {row[DESC_TRAMITE_INDEX] if len(row) > DESC_TRAMITE_INDEX else 'N/A'}")

                    item = CaseNotebookItem(
                        folio_number=folio_number,
                        document=row[DOC_COLUMN_INDEX] if len(row) > DOC_COLUMN_INDEX else "",
                        stage=row[STAGE_COLUMN_INDEX] if len(row) > STAGE_COLUMN_INDEX else "",
                        procedure=row[PROCEDURE_COLUMN_INDEX] if len(row) > PROCEDURE_COLUMN_INDEX else "",
                        procedure_description=row[DESC_TRAMITE_INDEX] if len(row) > DESC_TRAMITE_INDEX else "",
                        procedure_date=row[DATE_COLUMN_INDEX] if len(row) > DATE_COLUMN_INDEX else "",
                        page=page,
                        milestone=milestone
                    )

                    items.append(item)
                except (ValueError, IndexError) as e:
                    logging.warning(f"Error parsing row data: {e}, row: {row}")
                    continue

        self._log_milestone_summary(items)
        
        return items, milestone_events

    def _log_milestone_summary(self, items: list[CaseNotebookItem]) -> None:
        """Log summary of milestones found in items."""
        hitos_count = {}
        for item in items:
            if item.milestone:
                hitos_count[item.milestone] = hitos_count.get(item.milestone, 0) + 1
        
        total_hitos = len([item for item in items if item.milestone])
        logging.info(f">>> Total de hitos encontrados: {total_hitos}")

        if hitos_count:
            logging.info(">>> Resumen de hitos encontrados:")
            def hito_sort_key(hito_item):
                hito_name = hito_item[0]
                match = re.search(r'Hito (\d+)\.(\d+)', hito_name)
                if match:
                    return (int(match.group(1)), int(match.group(2)))
                else:
                    match = re.search(r'Hito (\d+)', hito_name)
                    if match:
                        return (int(match.group(1)), 0)
                return (0, 0)
            
            for hito, count in sorted(hitos_count.items(), key=hito_sort_key):
                logging.info(f"   {hito}: {count} ocurrencia(s)")
        else:
            logging.info(">>> No se encontraron hitos en los datos")

    def save_folios_to_db(self, items: list[CaseNotebookItem], case_number: str, year: int, save_to_db: bool = False) -> dict:
        """Save folios to database if save_to_db is True. Skip existing folios."""
        if not save_to_db:
            logging.info(">>> Guardado en BD deshabilitado (save_to_db=False)")
            return {"saved": 0, "skipped": 0}
        
        if not items:
            logging.warning(">>> No hay folios para guardar en la base de datos")
            return {"saved": 0, "skipped": 0}
        
        logging.info(f">>> Iniciando guardado en BD: {len(items)} folios para ROL {case_number}, AÑO {year}")
        
        saved_count = 0
        skipped_count = 0
        session = next(get_session())
        
        try:
            scraping_session_id = datetime.now().strftime("%Y-%m-%d-%H")
            logging.info(f">>> Sesión de scraping: {scraping_session_id}")
            
            for i, item in enumerate(items, 1):
                
                existing_folio = session.query(PJUDFolio).filter(
                    PJUDFolio.folio_number == item.folio_number,
                    PJUDFolio.case_number == case_number,
                    PJUDFolio.year == year,
                    PJUDFolio.procedure_description == item.procedure_description
                ).first()
                
                if existing_folio:
                    skipped_count += 1
                else:
                    new_folio = PJUDFolio(
                        folio_number=item.folio_number,
                        case_number=case_number,
                        year=year,
                        document=item.document,
                        stage=item.stage,
                        procedure=item.procedure,
                        procedure_description=item.procedure_description,
                        procedure_date=parse_procedure_date(item.procedure_date),
                        page=item.page,
                        milestone=item.milestone,
                        scraping_session_id=scraping_session_id,
                        scraping_type="full"
                    )
                    session.add(new_folio)
                    saved_count += 1
            session.commit()
            logging.info(">>> 💾 Transacción de BD confirmada exitosamente")
            
            total_processed = saved_count + skipped_count
            logging.info(f">>> 📊 RESUMEN FINAL BD:")
            logging.info(f">>>    Total procesados: {total_processed}")
            logging.info(f">>>    ✅ Nuevos guardados: {saved_count}")
            logging.info(f">>>    ❌ Existentes omitidos: {skipped_count}")
            logging.info(f">>>    ROL: {case_number}, AÑO: {year}")
            
        except Exception as e:
            session.rollback()
            logging.error(f">>> 💥 ERROR CRÍTICO al guardar en BD:")
            logging.error(f">>>    Error: {e}")
            logging.error(f">>>    ROL: {case_number}, AÑO: {year}")
            logging.error(f">>>    Folios procesados antes del error: {saved_count + skipped_count}/{len(items)}")
            logging.error(">>> 🔄 Transacción revertida - no se guardaron cambios")
            raise
        finally:
            session.close()
            logging.info(">>> 🔌 Conexión a BD cerrada")
        
        return {"saved": saved_count, "skipped": skipped_count}

    async def extract_case_notebook(self, request: CaseNotebookRequest) -> CaseNotebookResponse:
        """Main method to extract case notebook information"""
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(
                    headless=self.headless,
                    args=[
                        '--disable-gpu',
                        '--disable-dev-shm-usage',
                        '--disable-web-security',
                        '--disable-features=VizDisplayCompositor',
                        '--no-sandbox',
                        '--disable-setuid-sandbox'
                    ]
                )

                context = await browser.new_context(
                    viewport={"width": 1366, "height": 900},
                    user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    locale='es-CL',
                    timezone_id='America/Santiago'
                )
                page = await context.new_page()

                try:
                    await page.goto(PJUD_URL, wait_until="domcontentloaded", timeout=30000)
                except TimeoutError:
                    logging.error("Timeout cargando home.")
                    return CaseNotebookResponse(message="Timeout cargando página principal", status=500, data=[], total_items=0)

                await self.close_modal_if_present(page)
                await page.wait_for_timeout(500)

                if not await self.click_fast(page, r"^\s*Consulta\s+causas\s*$"):
                    await self.click_fast(page, r"Ingreso\s+como\s+invitado")
                await page.wait_for_timeout(300)

                await self.click_fast(page, r"B(ú|u)squeda\s+por\s+RIT")
                await page.wait_for_timeout(1000)  # Aumentar tiempo de espera

                # Buscar select de Competencia con reintentos
                competencia = None
                max_attempts = 5
                for attempt in range(max_attempts):
                    logging.info(f">>> 🔍 Buscando select de Competencia (intento {attempt + 1}/{max_attempts})...")
                    competencia = await self.find_select_by_label(page, r"Competencia")
                    if competencia:
                        logging.info(f">>> ✅ Select de Competencia encontrado en intento {attempt + 1}")
                        break
                    else:
                        logging.warning(f">>> ⚠️ Select de Competencia no encontrado en intento {attempt + 1}")
                        if attempt < max_attempts - 1:
                            await page.wait_for_timeout(2000)  # Esperar 2 segundos antes del siguiente intento
                
                if not competencia:
                    raise RuntimeError("No encontré el select de Competencia después de múltiples intentos.")

                await self.wait_select_ready(page, competencia, min_options=2, timeout_ms=5000)  # Aumentar timeout
                await self.select_by_label_text(page, competencia, [r"^\s*Civil\s*$"], fast_mode=True)

                tipo = await self.find_select_by_label(page, r"Tipo\s*B(ú|u)squeda")
                if tipo:
                    if await self.wait_select_ready(page, tipo, min_options=2, timeout_ms=2000):
                        await self.select_by_label_text(page, tipo, [
                            r"Recurso\s+.*Corte\s+de\s+Apelaciones",
                            r"Causa\s+.*Juzgado",
                            r"RIT",
                            r"Civil"
                        ], fast_mode=True)

                corte = await self.find_select_by_label(page, r"^Corte")
                if not corte:
                    raise RuntimeError("No encontré el select de Corte.")
                if not await self.wait_select_ready(page, corte, min_options=2, timeout_ms=3000):
                    raise RuntimeError("Corte no se habilitó/cargó (revisa Tipo Búsqueda).")
                await self.select_by_label_text(page, corte, [
                    r"C\.?A\.?\s*Santiago",
                    r"Corte\s+de\s+Apelaciones\s+de\s+Santiago",
                    r"\bSantiago\b"
                ], fast_mode=True)

                tribunal = await self.find_select_by_label(page, r"Tribunal")
                if not tribunal:
                    raise RuntimeError("No encontré el select de Tribunal.")
                if not await self.wait_select_ready(page, tribunal, min_options=2, timeout_ms=3000):
                    raise RuntimeError("Tribunal no se habilitó/cargó tras Corte.")
                
                try:
                    tribunal_name = self.get_tribunal_name_by_id(request.tribunal_id)
                    logging.info(f">>> 🏛️ TRIBUNAL SELECCIONADO:")
                    logging.info(f">>>    ID: {request.tribunal_id}")
                    logging.info(f">>>    Nombre: {tribunal_name}")
                    
                    if request.debug:
                        logging.info(f">>> Seleccionando tribunal: {tribunal_name} (ID: {request.tribunal_id})")
                    
                    tribunal_patterns = self.generate_tribunal_patterns(tribunal_name)
                    logging.info(f">>> 🔍 PATRONES DE BÚSQUEDA GENERADOS:")
                    for i, pattern in enumerate(tribunal_patterns, 1):
                        logging.info(f">>>    Patrón {i}: {pattern}")
                    
                    if request.debug:
                        logging.info(f">>> Patrones de búsqueda: {tribunal_patterns}")
                except ValueError as e:
                    logging.error(f">>> ❌ ERROR: Tribunal ID inválido: {e}")
                    raise RuntimeError(f"Tribunal ID inválido: {e}")
                
                logging.info(f">>> 🎯 SELECCIONANDO TRIBUNAL EN LA PÁGINA:")
                logging.info(f">>>    Buscando: {tribunal_name}")
                await self.select_by_label_text(page, tribunal, tribunal_patterns, fast_mode=True)
                logging.info(f">>> ✅ Tribunal seleccionado exitosamente")

                libro = await self.find_select_by_label(page, r"(Libro|Tipo|Letra)")
                if libro and await self.wait_select_ready(page, libro, min_options=2, timeout_ms=2000):
                    await self.select_by_label_text(page, libro, [r"^\s*C\s*$", r"\bC\b"], fast_mode=True)
                else:
                    try:
                        await page.get_by_label(re.compile(r"(Libro|Tipo|Letra)", re.I)).fill("C")
                    except Exception:
                        pass

                await self.fill_input_fast(page, r"^Rol$", request.case_number)
                await self.fill_input_fast(page, r"A(ñ|n)o", request.year)

                if not await self.click_by_text(page, r"^\s*Buscar\s*$", role="button"):
                    await self.click_by_text(page, r"^\s*Consultar\s*$", role="button")

                await page.wait_for_load_state("domcontentloaded")
                
                try:
                    logging.info(">>> Esperando a que la tabla se cargue...")
                    await page.wait_for_selector("#dtaTableDetalle:visible", timeout=15000)
                    logging.info(">>> Tabla encontrada, esperando estabilización...")
                    await page.wait_for_timeout(2000)
                    
                    detalle_button = page.locator("#dtaTableDetalle tr:first-child td[align='center'] a.toggle-modal")
                    
                    if await detalle_button.count() > 0:
                        href = await detalle_button.get_attribute("href")
                        clase = await detalle_button.get_attribute("class")
                        
                        if href == "#modalDetalleCivil" and "toggle-modal" in clase:
                            await detalle_button.click(timeout=2000)
                            logging.info(">>> Clic en botón de detalle exitoso")
                            
                            logging.info(">>> Esperando a que el modal se abra...")
                            await page.wait_for_selector(".modal.in", timeout=5000)
                            await page.wait_for_timeout(500)
                            
                            items, milestone_events = await self.extract_table_data(page)
                            
                            if request.save_to_db:
                                if items:
                                    logging.info(f">>> 🗄️ Iniciando proceso de guardado en BD...")
                                    try:
                                        db_result = self.save_folios_to_db(
                                            items, 
                                            request.case_number, 
                                            request.year, 
                                            save_to_db=True
                                        )
                                        logging.info(f">>> 🎯 PROCESO BD COMPLETADO:")
                                        logging.info(f">>>    ✅ {db_result['saved']} folios nuevos guardados")
                                        logging.info(f">>>    ❌ {db_result['skipped']} folios existentes omitidos")
                                        logging.info(f">>>    📋 Total folios procesados: {len(items)}")
                                    except Exception as e:
                                        logging.error(f">>> 💥 FALLO CRÍTICO en guardado BD:")
                                        logging.error(f">>>    Error: {e}")
                                        logging.error(f">>>    ROL: {request.case_number}, AÑO: {request.year}")
                                        logging.error(">>> ⚠️ Continuando sin guardar en BD...")

                                else:
                                    logging.warning(">>> ⚠️ No hay folios para guardar en BD (lista vacía)")
                            else:
                                logging.info(">>> ℹ️ Guardado en BD deshabilitado por configuración")

                            await browser.close()
                            logging.info(">>> 🔌 Browser cerrado, iniciando procesamiento de PDFs...")

                            if milestone_events:
                                case_id = getattr(self, '_current_case_id', None)
                                logging.info(">>> 🔄 INICIANDO PROCESAMIENTO DE EVENTOS...")
                                logging.info(f">>> 📥 Total eventos a procesar: {len(milestone_events)}")
                                
                                # Separar eventos con PDF de eventos sin PDF
                                events_with_pdf = [event for event in milestone_events if event.get('pdf_path') is not None]
                                events_without_pdf = [event for event in milestone_events if event.get('pdf_path') is None]
                                
                                logging.info(f">>> 📋 Eventos con PDF: {len(events_with_pdf)}")
                                logging.info(f">>> 📋 Eventos sin PDF: {len(events_without_pdf)}")
                                
                                # Procesar eventos con PDF
                                if events_with_pdf:
                                    logging.info(">>> 🔄 PROCESANDO EVENTOS CON PDF...")
                                    await self.process_downloaded_pdfs(events_with_pdf, case_id)
                                    logging.info(">>> ✅ PROCESAMIENTO DE EVENTOS CON PDF COMPLETADO")
                                
                                # Procesar eventos sin PDF
                                if events_without_pdf:
                                    logging.info(">>> 🔄 PROCESANDO EVENTOS SIN PDF...")
                                    await self.process_events_without_pdf(events_without_pdf, case_id)
                                    logging.info(">>> ✅ PROCESAMIENTO DE EVENTOS SIN PDF COMPLETADO")
                                
                                logging.info(">>> ✅ PROCESAMIENTO DE TODOS LOS EVENTOS COMPLETADO")
                            else:
                                logging.info(">>> ℹ️ No hay eventos para procesar")
                            
                            return CaseNotebookResponse(
                                message="Success", 
                                status=200, 
                                data=items, 
                                total_items=len(items)
                            )
                        else:
                            logging.warning(">>> El elemento encontrado no es el botón de detalle correcto")
                    else:
                        logging.warning(">>> No se encontró el botón de detalle")
                        
                except Exception as e:
                    logging.error(f">>> Error al hacer clic en detalle: {e}")
                
                await browser.close()
                return CaseNotebookResponse(message="No se encontraron datos", status=404, data=[], total_items=0)
                
        except Exception as e:
            logging.error(f"Failed to extract case notebook: {e}")
            return CaseNotebookResponse(message=f"Internal error: {e}", status=500, data=[], total_items=0)

    def _find_milestone_rows(self, hitos_data: list[list[str]]) -> list[tuple[int, int, str]]:
        """Find all milestone rows (Hito 3, 4, 5, 6, 7). Returns (scraping_index, data_index, milestone_type)."""
        milestones = []
        for i, row in enumerate(hitos_data):
            if len(row) > DESC_TRAMITE_INDEX:
                desc_tramite = row[DESC_TRAMITE_INDEX].lower().strip()
                milestone = row[-1] if len(row) > DESC_TRAMITE_INDEX else None
                
                # Índice para scraping (invertido) y índice para datos (directo)
                scraping_index = len(hitos_data) - 1 - i  # Para acceder a documentos correctamente
                data_index = i  # Para obtener los datos correctos de la fila
                
                if milestone == "Hito 3":
                    logging.info(f">>> ✅ Encontrado Hito 3 en fila {i+1} (scraping: {scraping_index}, datos: {data_index}): '{desc_tramite}'")
                    milestones.append((scraping_index, data_index, "hito3"))
                elif milestone and milestone.startswith("Hito 4"):
                    logging.info(f">>> ✅ Encontrado {milestone} en fila {i+1} (scraping: {scraping_index}, datos: {data_index}): '{desc_tramite}'")
                    milestones.append((scraping_index, data_index, "hito4"))
                elif milestone == "Hito 5":
                    logging.info(f">>> ✅ Encontrado Hito 5 en fila {i+1} (scraping: {scraping_index}, datos: {data_index}): '{desc_tramite}'")
                    milestones.append((scraping_index, data_index, "hito5"))
                elif milestone == "Hito 6":
                    logging.info(f">>> ✅ Encontrado Hito 6 en fila {i+1} (scraping: {scraping_index}, datos: {data_index}): '{desc_tramite}'")
                    milestones.append((scraping_index, data_index, "hito6"))
                elif milestone == "Hito 7b":
                    logging.info(f">>> ✅ Encontrado Hito 7b en fila {i+1} (scraping: {scraping_index}, datos: {data_index}): '{desc_tramite}'")
                    milestones.append((scraping_index, data_index, "hito7b"))
                elif milestone == "Hito 7a":
                    logging.info(f">>> ✅ Encontrado Hito 7a en fila {i+1} (scraping: {scraping_index}, datos: {data_index}): '{desc_tramite}'")
                    milestones.append((scraping_index, data_index, "hito7a"))
        return milestones

    async def _find_download_button(self, doc_cell) -> Optional[Locator]:
        """Find download button in document cell."""
        selectors = ["a", "button", "[onclick*='download']", "[onclick*='pdf']", "img[src*='pdf']", "img[src*='download']"]
        
        for selector in selectors:
            button = doc_cell.locator(selector).first
            if await button.count() > 0:
                logging.info(f">>> 🔍 Botón encontrado con selector: {selector}")
                return button
        return None


    async def _download_pdf_from_new_tab(self, page, download_button, milestone_type: str, debug: bool = False) -> Optional[str]:
        """Download PDF by constructing URL from form input."""
        try:
            logging.info(">>> 🔍 Obteniendo form que contiene el botón de descarga...")
            
            # Obtener el form que contiene el botón
            form = download_button.locator('xpath=ancestor::form').first
            if await form.count() == 0:
                logging.error(">>> ❌ No se encontró el form que contiene el botón")
                return None
            
            logging.info(">>> ✅ Form encontrado")
            
            # Extraer el action del form
            form_action = await form.get_attribute('action')
            if not form_action:
                logging.error(">>> ❌ No se encontró el atributo 'action' en el form")
                return None
            
            logging.info(f">>> 📋 Form action: {form_action}")
            
            # Extraer el valor del input hidden dtaDoc
            dta_doc_input = form.locator('input[name="dtaDoc"]').first
            if await dta_doc_input.count() == 0:
                logging.error(">>> ❌ No se encontró el input hidden 'dtaDoc' en el form")
                return None
            
            dta_doc_value = await dta_doc_input.get_attribute('value')
            if not dta_doc_value:
                logging.error(">>> ❌ No se encontró el valor del input hidden 'dtaDoc'")
                return None
            
            logging.info(f">>> ✅ Valor dtaDoc obtenido (longitud: {len(dta_doc_value)} caracteres)")
            
            # Construir la URL manualmente
            base_url = "https://oficinajudicialvirtual.pjud.cl"
            # Si el action no comienza con /, agregarlo
            if not form_action.startswith('/'):
                form_action = '/' + form_action
            
            current_url = f"{base_url}{form_action}?dtaDoc={dta_doc_value}"
            logging.info(f">>> 🔗 URL construida: {current_url}")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{milestone_type}_{timestamp}.pdf"
            download_path = f"/tmp/{filename}"
            
            cookies = await page.context.cookies()
            cookie_header = "; ".join([f"{cookie['name']}={cookie['value']}" for cookie in cookies])
            
            logging.info(f">>> 🍪 Usando cookies para descarga: {len(cookies)} cookies")
            
            headers = {
                'Cookie': cookie_header,
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'none',
                'Cache-Control': 'max-age=0',
            }

            async with aiohttp.ClientSession() as session:
                logging.info(f">>> 📡 Haciendo HEAD request para detectar tipo de contenido...")
                async with session.head(current_url, headers=headers, allow_redirects=True, timeout=aiohttp.ClientTimeout(total=30)) as head_response:
                    head_response.raise_for_status()
                    content_type = head_response.headers.get('Content-Type', '').lower()
                    logging.info(f">>> 📋 Content-Type: {content_type}")

                    if 'application/pdf' in content_type:
                        logging.info(">>> 📄 PDF detectado, descargando...")
                        async with session.get(current_url, headers=headers, allow_redirects=True, timeout=aiohttp.ClientTimeout(total=30)) as pdf_response:
                            pdf_response.raise_for_status()
                            
                            pdf_content = await pdf_response.read()
                            
                            if pdf_content[:4] == b'%PDF':
                                logging.info(">>> ✅ Firma PDF verificada")
                                
                                with open(download_path, 'wb') as f:
                                    f.write(pdf_content)
                                
                                milestone_name = "Hito 3 (Ordena despachar mandamiento)" if milestone_type == "hito3" else "Hito 5 (Opone excepciones)"
                                logging.info(f">>> ✅ PDF de {milestone_name} descargado: {download_path}")
                                
                                if os.path.exists(download_path):
                                    file_size = os.path.getsize(download_path)
                                    logging.info(f">>> 📊 Tamaño del archivo: {file_size} bytes")
                                    return download_path
                                else:
                                    logging.error(">>> ❌ El archivo no se guardó correctamente")
                                    return None
                            else:
                                logging.error(">>> ❌ El archivo descargado no es un PDF válido (firma no encontrada)")
                                return None
                    else:
                        logging.error(f">>> ❌ El contenido no es un PDF. Content-Type: {content_type}")
                        return None
                        
        except aiohttp.ClientError as e:
            logging.error(f">>> ❌ Error HTTP al descargar PDF: {e}")
            if debug:
                logging.error(f">>> 🔍 Traceback completo: {traceback.format_exc()}")
            return None
        except Exception as e:
            logging.error(f">>> ❌ ERROR CRÍTICO AL DESCARGAR PDF:")
            logging.error(f">>>    🚨 Error: {e}")
            logging.error(f">>>    📄 Milestone: {milestone_type}")
            logging.error(f">>>    📄 PDF esperado: {milestone_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            if debug:
                logging.error(f">>> 🔍 Traceback completo: {traceback.format_exc()}")
            return None

    async def process_milestone_events(self, page, modal_table, rows_data, case_id: str = None, case_number: str = None, year: int = None, debug: bool = False) -> list[dict]:
        """Process milestone events: download PDFs for Hito 3 and 5, create entries for Hito 4, 6, and 7"""
        try:
            logging.info(">>> 🔍 INICIANDO PROCESAMIENTO DE HITOS...")
            logging.info(">>> 🎯 Buscando todos los hitos relevantes...")
            logging.info(f">>> 🆔 Case ID: {case_id}")
            logging.info(f">>> 📋 Case Number: {case_number}")
            logging.info(f">>> 📅 Year: {year}")
            logging.info(f">>> 🐛 Debug mode: {debug}")
            
            milestones = self._find_milestone_rows(rows_data)
            logging.info(f">>> 📊 HITOS ENCONTRADOS: {len(milestones)}")
            
            if not milestones:
                logging.warning(">>> ⚠️ NO SE ENCONTRARON HITOS VÁLIDOS:")
                logging.warning(">>>    - Hito 3: 'Ordena despachar mandamiento' (con PDF)")
                logging.warning(">>>    - Hito 4: 'Notificación' (sin PDF)")
                logging.warning(">>>    - Hito 5: 'Opone excepciones' (con PDF)")
                logging.warning(">>>    - Hito 6: 'Evacua traslado' (sin PDF)")
                logging.warning(">>>    - Hito 7a: 'Recibe la causa a prueba' (sin PDF)")
                logging.warning(">>>    - Hito 7b: 'Sentencia' (sin PDF)")
                logging.warning(f">>>    - Total filas analizadas: {len(rows_data)}")
                return []
            
            logging.info(f">>> ✅ HITOS ENCONTRADOS: {len(milestones)}")
            for i, (scraping_index, data_index, milestone_type) in enumerate(milestones):
                logging.info(f">>>    {i+1}. {milestone_type.upper()} (scraping: fila {scraping_index + 1}, datos: fila {data_index + 1})")
            
            # Ordenar los hitos por data_index para procesarlos en orden cronológico correcto
            milestones_sorted = sorted(milestones, key=lambda x: x[1])  # Ordenar por data_index
            logging.info(f">>> 🔄 HITOS ORDENADOS CRONOLÓGICAMENTE:")
            for i, (scraping_index, data_index, milestone_type) in enumerate(milestones_sorted):
                logging.info(f">>>    {i+1}. {milestone_type.upper()} (scraping: fila {scraping_index + 1}, datos: fila {data_index + 1})")
            
            milestone_events = []
            logging.info(f">>> 🔄 INICIANDO PROCESAMIENTO DE {len(milestones_sorted)} EVENTOS...")
            
            for i, (scraping_index, data_index, milestone_type) in enumerate(milestones_sorted):
                logging.info(f">>> 🔄 PROCESANDO HITO {i+1}/{len(milestones_sorted)}: {milestone_type.upper()}")
                logging.info(f">>> 📍 Fila scraping: {scraping_index + 1}, Fila datos: {data_index + 1}")
                logging.info(f">>> 📝 Descripción: {rows_data[data_index][DESC_TRAMITE_INDEX] if len(rows_data[data_index]) > DESC_TRAMITE_INDEX else 'N/A'}")
                
                # Verificar si el folio ya existe en la BD (para TODOS los hitos)
                logging.info(f">>> 🔍 Verificando si folio ya existe en BD...")
                if self._folio_already_exists(rows_data[data_index], case_number, year):
                    logging.info(f">>> ⏭️ HITO {milestone_type.upper()} ya existe en BD - OMITIENDO procesamiento")
                    continue
                
                # HITOS SIN PDF - Solo crear evento (no descargar PDF)
                if milestone_type in HITOS_SIN_PDF:
                    logging.info(f">>> 🎯 {milestone_type.upper()} DETECTADO: No necesita descargar PDF")
                    logging.info(f">>> 📝 Creando entrada para procesamiento posterior...")
                    
                    # Crear entrada para procesamiento posterior (sin PDF)
                    pdf_info = {
                        "milestone_type": milestone_type,
                        "case_id": case_id,
                        "description": rows_data[data_index][DESC_TRAMITE_INDEX] if len(rows_data[data_index]) > DESC_TRAMITE_INDEX else 'N/A',
                        "pdf_path": None,  # No hay PDF para estos hitos
                        "row_index": data_index,  # Usar data_index para obtener los datos correctos
                        "procedure_date": rows_data[data_index][DATE_COLUMN_INDEX] if len(rows_data[data_index]) > DATE_COLUMN_INDEX else None
                    }
                    milestone_events.append(pdf_info)
                    logging.info(f">>> ✅ {milestone_type.upper()} agregado para procesamiento posterior")
                    continue
                
                logging.info(f">>> ✅ Folio no existe - PROCEDIENDO CON PROCESAMIENTO")
                logging.info(f">>> 🔄 PROCESANDO HITO {i+1}/{len(milestones_sorted)}: {milestone_type.upper()}")
                
                pdf_info = await self._download_single_milestone_pdf(page, modal_table, rows_data, scraping_index, data_index, milestone_type, case_id, debug)
                if pdf_info:
                    milestone_events.append(pdf_info)
                    logging.info(f">>> ✅ PDF {i+1} descargado exitosamente: {pdf_info.get('pdf_path', 'unknown')}")
                else:
                    logging.error(f">>> ❌ FALLO en descarga de PDF {i+1}")
            
            logging.info(f">>> 📥 RESUMEN DE PROCESAMIENTO COMPLETADO:")
            logging.info(f">>>    Total eventos procesados: {len(milestone_events)}")
            logging.info(f">>>    Total hitos procesados: {len(milestones)}")
            
            return milestone_events
                
        except Exception as e:
            logging.error(f">>> ❌ ERROR CRÍTICO AL DESCARGAR PDFs DE HITOS:")
            logging.error(f">>>    🚨 Error: {e}")
            logging.error(f">>>    📊 Total hitos encontrados: {len(milestones) if 'milestones' in locals() else 'N/A'}")
            logging.error(f">>>    📋 Case Number: {case_number}")
            logging.error(f">>>    📅 Year: {year}")
            logging.error(f">>>    🆔 Case ID: {case_id}")
            if debug:
                logging.error(f">>> 🔍 Traceback completo: {traceback.format_exc()}")
            return []
    
    async def _download_single_milestone_pdf(self, page, modal_table, rows_data, scraping_index, data_index, milestone_type, case_id, debug) -> dict:
        """Download PDF for a single milestone (without processing)."""
        try:
            logging.info(f">>> 🔍 DESCARGANDO {milestone_type.upper()}:")
            logging.info(f">>>    📍 Fila scraping: {scraping_index + 1}, Fila datos: {data_index + 1}")
            logging.info(f">>>    📝 Descripción: {rows_data[data_index][DESC_TRAMITE_INDEX] if len(rows_data[data_index]) > DESC_TRAMITE_INDEX else 'N/A'}")
            
            logging.info(f">>> 🔍 LOCALIZANDO FILA EN TABLA...")
            rows = modal_table.locator("tbody tr")
            target_row = rows.nth(scraping_index)  # Usar scraping_index para acceder a la fila correcta en la tabla
            logging.info(f">>> ✅ Fila localizada en tabla")
            
            logging.info(f">>> 🔍 BUSCANDO BOTÓN DE DESCARGA en columna Doc. (índice {DOC_COLUMN_INDEX})...")
            doc_cell = target_row.locator("td").nth(DOC_COLUMN_INDEX)
            
            download_button = await self._find_download_button(doc_cell)
            
            if download_button and await download_button.count() > 0:
                logging.info(">>> ✅ BOTÓN DE DESCARGA ENCONTRADO")
                logging.info(">>> 🔄 INICIANDO DESCARGA DESDE NUEVA PESTAÑA...")
                
                try:
                    download_path = await self._download_pdf_from_new_tab(page, download_button, milestone_type, debug)
                    
                    if download_path:
                        logging.info(f">>> ✅ PDF DESCARGADO EXITOSAMENTE: {download_path}")
                        return {
                            "pdf_path": download_path,
                            "milestone_type": milestone_type,
                            "case_id": case_id,
                            "description": rows_data[data_index][DESC_TRAMITE_INDEX] if len(rows_data[data_index]) > DESC_TRAMITE_INDEX else 'N/A',
                            "procedure_date": rows_data[data_index][DATE_COLUMN_INDEX] if len(rows_data[data_index]) > DATE_COLUMN_INDEX else None
                        }
                    else:
                        logging.error(">>> ❌ FALLO EN DESCARGA: No se obtuvo ruta del PDF")
                        return None
                        
                except Exception as e:
                    logging.error(f">>> ❌ ERROR EN DESCARGA DE PDF:")
                    logging.error(f">>>    🚨 Error: {e}")
                    logging.error(f">>>    📍 Milestone: {milestone_type}")
                    logging.error(f">>>    🆔 Case ID: {case_id}")
                    logging.error(f">>>    📄 PDF esperado: {milestone_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
                    logging.error(f">>>    📝 Descripción: {rows_data[data_index][DESC_TRAMITE_INDEX] if len(rows_data[data_index]) > DESC_TRAMITE_INDEX else 'N/A'}")
                    if debug:
                        logging.error(f">>> 🔍 Traceback completo: {traceback.format_exc()}")
                    return None
                    
            else:
                logging.error(">>> ❌ NO SE ENCONTRÓ BOTÓN DE DESCARGA:")
                logging.error(f">>>    📍 Fila scraping: {scraping_index + 1}, Fila datos: {data_index + 1}")
                logging.error(f">>>    📝 Descripción: {rows_data[data_index][DESC_TRAMITE_INDEX] if len(rows_data[data_index]) > DESC_TRAMITE_INDEX else 'N/A'}")
                logging.error(f">>>    🎯 Milestone: {milestone_type}")
                logging.error(f">>>    🆔 Case ID: {case_id}")
                logging.error(f">>>    📄 Columna Doc. (índice {DOC_COLUMN_INDEX}): {rows_data[data_index][DOC_COLUMN_INDEX] if len(rows_data[data_index]) > DOC_COLUMN_INDEX else 'N/A'}")
                logging.error(f">>>    🔍 Posibles causas:")
                logging.error(f">>>       - El documento no tiene botón de descarga")
                logging.error(f">>>       - El botón tiene un selector diferente")
                logging.error(f">>>       - El documento no está disponible")
                return None
                
        except Exception as e:
            logging.error(f">>> ❌ ERROR CRÍTICO AL DESCARGAR HITO {milestone_type.upper()}:")
            logging.error(f">>>    🚨 Error: {e}")
            logging.error(f">>>    📍 Fila scraping: {scraping_index + 1}, Fila datos: {data_index + 1}")
            logging.error(f">>>    📝 Descripción: {rows_data[data_index][DESC_TRAMITE_INDEX] if len(rows_data[data_index]) > DESC_TRAMITE_INDEX else 'N/A'}")
            logging.error(f">>>    🆔 Case ID: {case_id}")
            logging.error(f">>>    📄 PDF esperado: {milestone_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            if debug:
                logging.error(f">>> 🔍 Traceback completo: {traceback.format_exc()}")
            return None
    
    def _folio_already_exists(self, row_data: list[str], case_number: str, year: int) -> bool:
        """Check if a folio already exists in the database."""
        try:
            if not case_number or not year:
                return False
            
            folio_number = int(row_data[FOLIO_COLUMN_INDEX]) if row_data[FOLIO_COLUMN_INDEX] and row_data[FOLIO_COLUMN_INDEX].isdigit() else 0
            procedure_description = row_data[DESC_TRAMITE_INDEX] if len(row_data) > DESC_TRAMITE_INDEX else ""
            
            session = next(get_session())
            try:
                existing_folio = session.exec(
                    select(PJUDFolio).where(
                        PJUDFolio.folio_number == folio_number,
                        PJUDFolio.case_number == case_number,
                        PJUDFolio.year == year,
                        PJUDFolio.procedure_description == procedure_description
                    )
                ).first()
                
                return existing_folio is not None
                
            finally:
                session.close()
                
        except Exception as e:
            logging.error(f">>> ❌ Error verificando folio existente: {e}")
            return False
    
    async def process_downloaded_pdfs(self, downloaded_pdfs: list[dict], case_id: str) -> None:
        """Process all downloaded PDFs in correct legal order: DISPATCH_RESOLUTION first, then DEMAND_EXCEPTION."""
        if not downloaded_pdfs:
            logging.info(">>> ℹ️ No hay PDFs para procesar")
            return
        
        # Separar PDFs por tipo de hito para procesar en orden correcto
        dispatch_resolution_pdfs = [pdf for pdf in downloaded_pdfs if pdf['milestone_type'] == 'hito3']
        demand_exception_pdfs = [pdf for pdf in downloaded_pdfs if pdf['milestone_type'] == 'hito5']
        
        logging.info(f">>> 📋 PDFs DISPATCH_RESOLUTION (Hito 3): {len(dispatch_resolution_pdfs)}")
        logging.info(f">>> 📋 PDFs DEMAND_EXCEPTION (Hito 5): {len(demand_exception_pdfs)}")
        
        # PASO 1: Procesar DISPATCH_RESOLUTION primero (Hito 3)
        if dispatch_resolution_pdfs:
            logging.info(f">>> 🎯 PASO 1: PROCESANDO DISPATCH_RESOLUTION (Hito 3) - {len(dispatch_resolution_pdfs)} PDFs")
            for i, pdf_info in enumerate(dispatch_resolution_pdfs, 1):
                await self._process_single_pdf(pdf_info, case_id, i, len(dispatch_resolution_pdfs), "DISPATCH_RESOLUTION")
        
        # PASO 2: Procesar DEMAND_EXCEPTION después (Hito 5)
        if demand_exception_pdfs:
            logging.info(f">>> 🎯 PASO 2: PROCESANDO DEMAND_EXCEPTION (Hito 5) - {len(demand_exception_pdfs)} PDFs")
            for i, pdf_info in enumerate(demand_exception_pdfs, 1):
                await self._process_single_pdf(pdf_info, case_id, i, len(demand_exception_pdfs), "DEMAND_EXCEPTION")
        
        logging.info(f">>> 🎯 PROCESAMIENTO DE PDFs COMPLETADO")
    
    async def process_events_without_pdf(self, events_without_pdf: list[dict], case_id: str) -> None:
        """Process events that don't require PDF processing (Hitos 4, 6, 7)."""
        if not events_without_pdf:
            logging.info(">>> ℹ️ No hay eventos sin PDF para procesar")
            return
        
        # Separar eventos por tipo
        hito4_events = [event for event in events_without_pdf if event['milestone_type'] == 'hito4']
        hito6_events = [event for event in events_without_pdf if event['milestone_type'] == 'hito6']
        hito7a_events = [event for event in events_without_pdf if event['milestone_type'] == 'hito7a']
        hito7b_events = [event for event in events_without_pdf if event['milestone_type'] == 'hito7b']
        
        logging.info(f">>> 📋 Eventos Hito 4: {len(hito4_events)}")
        logging.info(f">>> 📋 Eventos Hito 6: {len(hito6_events)}")
        logging.info(f">>> 📋 Eventos Hito 7a: {len(hito7a_events)}")
        logging.info(f">>> 📋 Eventos Hito 7b: {len(hito7b_events)}")
        
        # Procesar Hito 4 (NOTIFICATION - Evacua traslado)
        if hito4_events:
            logging.info(f">>> 🎯 PROCESANDO HITO 4 (NOTIFICATION) - {len(hito4_events)} eventos")
            for i, event_info in enumerate(hito4_events, 1):
                await self._process_notification_event(event_info, case_id, i, len(hito4_events))
        
        # Procesar Hito 6 (TRANSLATION_EVACUATION - Evacua traslado)
        if hito6_events:
            logging.info(f">>> 🎯 PROCESANDO HITO 6 (TRANSLATION_EVACUATION) - {len(hito6_events)} eventos")
            for i, event_info in enumerate(hito6_events, 1):
                await self._process_translation_evacuation_event(event_info, case_id, i, len(hito6_events))
        
        # Procesar Hito 7a (TRIAL_START - Recibe la causa a prueba)
        if hito7a_events:
            logging.info(f">>> 🎯 PROCESANDO HITO 7a (TRIAL_START) - {len(hito7a_events)} eventos")
            for i, event_info in enumerate(hito7a_events, 1):
                await self._process_trial_start_event(event_info, case_id, i, len(hito7a_events))
        
        # Procesar Hito 7b (SENTENCE - Sentencia)
        if hito7b_events:
            logging.info(f">>> 🎯 PROCESANDO HITO 7b (SENTENCE) - {len(hito7b_events)} eventos")
            for i, event_info in enumerate(hito7b_events, 1):
                await self._process_sentence_event(event_info, case_id, i, len(hito7b_events))
        
        logging.info(f">>> 🎯 PROCESAMIENTO DE EVENTOS SIN PDF COMPLETADO")
    
    async def _process_sentence_event(self, event_info: dict, case_id: str, index: int, total: int) -> None:
        """Process sentence event without PDF processing."""
        try:
            logging.info(f">>> 🔄 PROCESANDO SENTENCE {index}/{total}: {event_info['milestone_type'].upper()}")
            logging.info(f">>> 📄 Descripción: {event_info.get('description', 'N/A')}")
            logging.info(f">>> 🆔 Case ID: {case_id}")
            logging.info(f">>> 🎯 Tipo de hito: {event_info['milestone_type']}")
            
            session = next(get_session())
            logging.info(f">>> 🗄️ Conexión a BD establecida")
            
            try:
                logging.info(f">>> 🔍 PASO 1: Obteniendo caso de la BD...")
                case = self._get_case_by_id(session, case_id)
                if not case:
                    logging.error(f">>> ❌ PASO 1 FALLIDO: No se encontró el caso {case_id}")
                    return
                logging.info(f">>> ✅ PASO 1 EXITOSO: Caso encontrado - {case.title}")
                
                logging.info(f">>> 🔍 PASO 2: Creando evento SENTENCE...")
                procedure_date_str = event_info.get('procedure_date')
                procedure_date = parse_procedure_date(procedure_date_str) if procedure_date_str else None
                event = self._create_sentence_event(session, case, procedure_date)
                
                if not event:
                    logging.error(f">>> ❌ PASO 2 FALLIDO: No se pudo crear el evento SENTENCE")
                    return
                logging.info(f">>> ✅ PASO 2 EXITOSO: Evento SENTENCE creado - ID: {event.id}")
                
                logging.info(f">>> ✅ SENTENCE {index} procesado exitosamente")
                
            except Exception as e:
                logging.error(f">>> ❌ ERROR PROCESANDO SENTENCE {index}/{total}:")
                logging.error(f">>>    🚨 Error: {e}")
                logging.error(f">>>    📄 Descripción: {event_info.get('description', 'unknown')}")
                logging.error(f">>>    🎯 Milestone: {event_info.get('milestone_type', 'unknown')}")
                logging.error(f">>>    🆔 Case ID: {event_info.get('case_id', 'unknown')}")
                logging.error(f">>> ⚠️ Continuando con siguiente evento...")
            finally:
                session.close()
                
        except Exception as e:
            logging.error(f">>> ❌ ERROR CRÍTICO PROCESANDO SENTENCE {index}/{total}:")
            logging.error(f">>>    🚨 Error: {e}")
            logging.error(f">>>    📄 Descripción: {event_info.get('description', 'unknown')}")
            logging.error(f">>>    🎯 Milestone: {event_info.get('milestone_type', 'unknown')}")
            logging.error(f">>>    🆔 Case ID: {event_info.get('case_id', 'unknown')}")
            logging.error(f">>> ⚠️ Continuando con siguiente evento...")
    
    async def _process_trial_start_event(self, event_info: dict, case_id: str, index: int, total: int) -> None:
        """Process trial start event (Hito 7a - Recibe la causa a prueba) without PDF processing."""
        try:
            logging.info(f">>> 🔄 PROCESANDO TRIAL_START {index}/{total}: {event_info['milestone_type'].upper()}")
            logging.info(f">>> 📄 Descripción: {event_info.get('description', 'N/A')}")
            logging.info(f">>> 🆔 Case ID: {case_id}")
            logging.info(f">>> 🎯 Tipo de hito: {event_info['milestone_type']}")
            
            session = next(get_session())
            logging.info(f">>> 🗄️ Conexión a BD establecida")
            
            try:
                logging.info(f">>> 🔍 PASO 1: Obteniendo caso de la BD...")
                case = self._get_case_by_id(session, case_id)
                if not case:
                    logging.error(f">>> ❌ PASO 1 FALLIDO: No se encontró el caso {case_id}")
                    return
                logging.info(f">>> ✅ PASO 1 EXITOSO: Caso encontrado - {case.title}")
                
                logging.info(f">>> 🔍 PASO 2: Creando evento TRIAL_START...")
                procedure_date_str = event_info.get('procedure_date')
                procedure_date = parse_procedure_date(procedure_date_str) if procedure_date_str else None
                event = self._create_trial_start_event(session, case, procedure_date)
                
                if not event:
                    logging.error(f">>> ❌ PASO 2 FALLIDO: No se pudo crear el evento TRIAL_START")
                    return
                logging.info(f">>> ✅ PASO 2 EXITOSO: Evento TRIAL_START creado - ID: {event.id}")
                
                logging.info(f">>> ✅ TRIAL_START {index} procesado exitosamente")
                
            except Exception as e:
                logging.error(f">>> ❌ ERROR PROCESANDO TRIAL_START {index}/{total}:")
                logging.error(f">>>    🚨 Error: {e}")
                logging.error(f">>>    📄 Descripción: {event_info.get('description', 'unknown')}")
                logging.error(f">>>    🎯 Milestone: {event_info.get('milestone_type', 'unknown')}")
                logging.error(f">>>    🆔 Case ID: {event_info.get('case_id', 'unknown')}")
                logging.error(f">>> ⚠️ Continuando con siguiente evento...")
            finally:
                session.close()
                
        except Exception as e:
            logging.error(f">>> ❌ ERROR CRÍTICO PROCESANDO TRIAL_START {index}/{total}:")
            logging.error(f">>>    🚨 Error: {e}")
            logging.error(f">>>    📄 Descripción: {event_info.get('description', 'unknown')}")
            logging.error(f">>>    🎯 Milestone: {event_info.get('milestone_type', 'unknown')}")
            logging.error(f">>>    🆔 Case ID: {event_info.get('case_id', 'unknown')}")
            logging.error(f">>> ⚠️ Continuando con siguiente evento...")
    
    async def _process_notification_event(self, event_info: dict, case_id: str, index: int, total: int) -> None:
        """Process NOTIFICATION event (Hito 4 - Notificación) without PDF processing."""
        try:
            logging.info(f">>> 🔄 PROCESANDO NOTIFICATION {index}/{total}: {event_info['milestone_type'].upper()}")
            logging.info(f">>> 📄 Descripción: {event_info.get('description', 'N/A')}")
            logging.info(f">>> 🆔 Case ID: {case_id}")
            logging.info(f">>> 🎯 Tipo de hito: {event_info['milestone_type']}")
            
            session = next(get_session())
            logging.info(f">>> 🗄️ Conexión a BD establecida")
            
            try:
                logging.info(f">>> 🔍 PASO 1: Obteniendo caso de la BD...")
                case = self._get_case_by_id(session, case_id)
                if not case:
                    logging.error(f">>> ❌ PASO 1 FALLIDO: No se encontró el caso {case_id}")
                    return
                logging.info(f">>> ✅ PASO 1 EXITOSO: Caso encontrado - {case.title}")
                
                logging.info(f">>> 🔍 PASO 2: Creando evento NOTIFICATION...")
                procedure_date_str = event_info.get('procedure_date')
                procedure_date = parse_procedure_date(procedure_date_str) if procedure_date_str else None
                description = event_info.get('description')
                event = self._create_notification_event(session, case, procedure_date, description)
                
                if not event:
                    logging.error(f">>> ❌ PASO 2 FALLIDO: No se pudo crear el evento NOTIFICATION")
                    return
                logging.info(f">>> ✅ PASO 2 EXITOSO: Evento NOTIFICATION creado - ID: {event.id}")
                
                logging.info(f">>> ✅ NOTIFICATION {index} procesado exitosamente")
                
            except Exception as e:
                logging.error(f">>> ❌ ERROR PROCESANDO NOTIFICATION {index}/{total}:")
                logging.error(f">>>    🚨 Error: {e}")
                logging.error(f">>>    📄 Descripción: {event_info.get('description', 'unknown')}")
                logging.error(f">>>    🎯 Milestone: {event_info.get('milestone_type', 'unknown')}")
                logging.error(f">>>    🆔 Case ID: {event_info.get('case_id', 'unknown')}")
                logging.error(f">>> ⚠️ Continuando con siguiente evento...")
            finally:
                session.close()
                
        except Exception as e:
            logging.error(f">>> ❌ ERROR CRÍTICO PROCESANDO NOTIFICATION {index}/{total}:")
            logging.error(f">>>    🚨 Error: {e}")
            logging.error(f">>>    📄 Descripción: {event_info.get('description', 'unknown')}")
            logging.error(f">>>    🎯 Milestone: {event_info.get('milestone_type', 'unknown')}")
            logging.error(f">>>    🆔 Case ID: {event_info.get('case_id', 'unknown')}")
            logging.error(f">>> ⚠️ Continuando con siguiente evento...")
    
    async def _process_translation_evacuation_event(self, event_info: dict, case_id: str, index: int, total: int) -> None:
        """Process TRANSLATION_EVACUATION event (Hito 6 - Evacua traslado) without PDF processing."""
        try:
            logging.info(f">>> 🔄 PROCESANDO TRANSLATION_EVACUATION {index}/{total}: {event_info['milestone_type'].upper()}")
            logging.info(f">>> 📄 Descripción: {event_info.get('description', 'N/A')}")
            logging.info(f">>> 🆔 Case ID: {case_id}")
            logging.info(f">>> 🎯 Tipo de hito: {event_info['milestone_type']}")
            
            session = next(get_session())
            logging.info(f">>> 🗄️ Conexión a BD establecida")
            
            try:
                logging.info(f">>> 🔍 PASO 1: Obteniendo caso de la BD...")
                case = self._get_case_by_id(session, case_id)
                if not case:
                    logging.error(f">>> ❌ PASO 1 FALLIDO: No se encontró el caso {case_id}")
                    return
                logging.info(f">>> ✅ PASO 1 EXITOSO: Caso encontrado - {case.title}")
                
                logging.info(f">>> 🔍 PASO 2: Creando evento TRANSLATION_EVACUATION...")
                procedure_date_str = event_info.get('procedure_date')
                procedure_date = parse_procedure_date(procedure_date_str) if procedure_date_str else None
                event = self._create_translation_evacuation_event(session, case, procedure_date)
                
                if not event:
                    logging.error(f">>> ❌ PASO 2 FALLIDO: No se pudo crear el evento TRANSLATION_EVACUATION")
                    return
                logging.info(f">>> ✅ PASO 2 EXITOSO: Evento TRANSLATION_EVACUATION creado - ID: {event.id}")
                
                logging.info(f">>> ✅ TRANSLATION_EVACUATION {index} procesado exitosamente")
                
            except Exception as e:
                logging.error(f">>> ❌ ERROR PROCESANDO TRANSLATION_EVACUATION {index}/{total}:")
                logging.error(f">>>    🚨 Error: {e}")
                logging.error(f">>>    📄 Descripción: {event_info.get('description', 'unknown')}")
                logging.error(f">>>    🎯 Milestone: {event_info.get('milestone_type', 'unknown')}")
                logging.error(f">>>    🆔 Case ID: {event_info.get('case_id', 'unknown')}")
                logging.error(f">>> ⚠️ Continuando con siguiente evento...")
            finally:
                session.close()
                
        except Exception as e:
            logging.error(f">>> ❌ ERROR CRÍTICO PROCESANDO TRANSLATION_EVACUATION {index}/{total}:")
            logging.error(f">>>    🚨 Error: {e}")
            logging.error(f">>>    📄 Descripción: {event_info.get('description', 'unknown')}")
            logging.error(f">>>    🎯 Milestone: {event_info.get('milestone_type', 'unknown')}")
            logging.error(f">>>    🆔 Case ID: {event_info.get('case_id', 'unknown')}")
            logging.error(f">>> ⚠️ Continuando con siguiente evento...")
    
    async def _process_single_pdf(self, pdf_info: dict, case_id: str, index: int, total: int, event_type: str) -> None:
        """Process a single PDF for the specified event type."""
        try:
            logging.info(f">>> 🔄 PROCESANDO PDF {index}/{total}: {pdf_info['milestone_type'].upper()}")
            logging.info(f">>> 📄 Archivo: {pdf_info['pdf_path']}")
            logging.info(f">>> 📝 Descripción: {pdf_info['description']}")
            logging.info(f">>> 🔄 PROCESANDO PDF PARA {event_type}-EVENT")
            logging.info(f">>> 📋 Flujo: {pdf_info['milestone_type']} → {event_type} → Sugerencias")
            logging.info(f">>> 📄 Archivo PDF: {pdf_info['pdf_path']}")
            logging.info(f">>> 🆔 Case ID: {case_id}")
            logging.info(f">>> 🎯 Tipo de hito: {pdf_info['milestone_type']}")
            logging.info(f">>> 🐛 Debug mode: False")
            
            # Guardar pdf_info en el objeto para acceso posterior
            self._current_pdf_info = pdf_info
            
            await self.process_downloaded_pdf(
                pdf_info['pdf_path'], 
                pdf_info['case_id'], 
                pdf_info['milestone_type'], 
                debug=False
            )
            logging.info(f">>> ✅ PDF {index} procesado exitosamente")
            
        except Exception as e:
            logging.error(f">>> ❌ ERROR PROCESANDO PDF {index}/{total}:")
            logging.error(f">>>    🚨 Error: {e}")
            logging.error(f">>>    📄 Archivo: {pdf_info.get('pdf_path', 'unknown')}")
            logging.error(f">>>    📝 Descripción: {pdf_info.get('description', 'unknown')}")
            logging.error(f">>>    🎯 Milestone: {pdf_info.get('milestone_type', 'unknown')}")
            logging.error(f">>>    🆔 Case ID: {pdf_info.get('case_id', 'unknown')}")
            logging.error(f">>>    🎯 Event Type: {event_type}")
            logging.error(f">>> ⚠️ Continuando con siguiente PDF...")
    
    def _get_case_by_id(self, session: Session, case_id: str) -> Optional[Case]:
        """Get case by ID from database."""
        case = session.exec(select(Case).where(Case.id == case_id)).first()
        if not case:
            logging.error(f">>> ❌ Case con ID {case_id} no encontrado")
            return None
        logging.info(f">>> ✅ Case encontrado: {case.title}")
        return case
    
    def _create_demand_exception_event(self, session: Session, case: Case, pdf_path: str, procedure_date: date = None) -> Optional[CaseEvent]:
        """Create demand exception event from PDF."""
        try:
            logging.info(f">>> 🔧 DEMAND-EXCEPTION-EVENT: Iniciando creación...")
            logging.info(f">>> 📄 PDF: {pdf_path}")
            logging.info(f">>> 🆔 Case: {case.title} (ID: {case.id})")
            if procedure_date:
                logging.info(f">>> 📅 Procedure Date: {procedure_date}")
            
            logging.info(f">>> 🔍 DEMAND-EXCEPTION: Creando EventManager...")
            event_manager = DemandExceptionEventManager(case)
            logging.info(f">>> ✅ DEMAND-EXCEPTION: EventManager creado")
            
            logging.info(f">>> 🔍 DEMAND-EXCEPTION: Extrayendo información del PDF...")
            information, event = event_manager.create_from_file_path(session, pdf_path, procedure_date)
            logging.info(f">>> ✅ DEMAND-EXCEPTION: Información extraída y evento creado")
            logging.info(f">>> 📝 DEMAND-EXCEPTION: Evento ID: {event.id}")
            logging.info(f">>> 📝 DEMAND-EXCEPTION: Título: {event.title}")
            logging.info(f">>> 📝 DEMAND-EXCEPTION: Tipo: {event.type}")
            
            logging.info(f">>> 🔍 DEMAND-EXCEPTION: Generando sugerencias...")
            event_manager.create_suggestions(session, event, information)
            logging.info(f">>> ✅ DEMAND-EXCEPTION: Sugerencias generadas")

            logging.info(f">>> 💾 DEMAND-EXCEPTION: Guardando cambios del caso...")
            session.add(case)
            session.commit()
            session.refresh(case)
            logging.info(f">>> ✅ DEMAND-EXCEPTION: Cambios guardados - Estado: {case.status}")
            
            logging.info(f">>> 🎯 DEMAND-EXCEPTION-EVENT COMPLETADO EXITOSAMENTE")
            return event
        except Exception as e:
            logging.error(f">>> ❌ DEMAND-EXCEPTION-EVENT FALLIDO:")
            logging.error(f">>>    Error: {e}")
            logging.error(f">>>    PDF: {pdf_path}")
            logging.error(f">>>    Case: {case.title} (ID: {case.id})")
            session.rollback()
            return None
    
    def _create_dispatch_resolution_event(self, session: Session, case: Case, pdf_path: str, procedure_date: date = None) -> Optional[CaseEvent]:
        """Create dispatch resolution event from PDF."""
        try:
            logging.info(f">>> 🔧 DISPATCH-RESOLUTION-EVENT: Iniciando creación...")
            logging.info(f">>> 📄 PDF: {pdf_path}")
            logging.info(f">>> 🆔 Case: {case.title} (ID: {case.id})")
            if procedure_date:
                logging.info(f">>> 📅 Procedure Date: {procedure_date}")
            
            logging.info(f">>> 🔍 DISPATCH-RESOLUTION: Creando EventManager...")
            event_manager = DispatchResolutionEventManager(case)
            logging.info(f">>> ✅ DISPATCH-RESOLUTION: EventManager creado")
            
            logging.info(f">>> 🔍 DISPATCH-RESOLUTION: Extrayendo información del PDF...")
            information, event = event_manager.create_from_file_path(session, pdf_path, procedure_date)
            logging.info(f">>> ✅ DISPATCH-RESOLUTION: Información extraída y evento creado")
            logging.info(f">>> 📝 DISPATCH-RESOLUTION: Evento ID: {event.id}")
            logging.info(f">>> 📝 DISPATCH-RESOLUTION: Título: {event.title}")
            logging.info(f">>> 📝 DISPATCH-RESOLUTION: Tipo: {event.type}")
            
            logging.info(f">>> 🔍 DISPATCH-RESOLUTION: Generando sugerencias...")
            event_manager.create_suggestions(session, event, information)
            logging.info(f">>> ✅ DISPATCH-RESOLUTION: Sugerencias generadas")

            logging.info(f">>> 💾 DISPATCH-RESOLUTION: Guardando cambios del caso...")
            session.add(case)
            session.commit()
            session.refresh(case)
            logging.info(f">>> ✅ DISPATCH-RESOLUTION: Cambios guardados - Estado: {case.status}")
            
            logging.info(f">>> 🎯 DISPATCH-RESOLUTION-EVENT COMPLETADO EXITOSAMENTE")
            return event
        except Exception as e:
            logging.error(f">>> ❌ DISPATCH-RESOLUTION-EVENT FALLIDO:")
            logging.error(f">>>    Error: {e}")
            logging.error(f">>>    PDF: {pdf_path}")
            logging.error(f">>>    Case: {case.title} (ID: {case.id})")
            session.rollback()
            return None
    
    def _create_sentence_event(self, session: Session, case: Case, procedure_date: date = None) -> Optional[CaseEvent]:
        """Create sentence event directly without PDF processing."""
        try:
            logging.info(f">>> 🔧 SENTENCE-EVENT: Iniciando creación...")
            logging.info(f">>> 🆔 Case: {case.title} (ID: {case.id})")
            if procedure_date:
                logging.info(f">>> 📅 Procedure Date: {procedure_date}")
            
            sentence_event = CaseEvent(
                id=uuid4(),
                case_id=case.id,
                case=case,
                title="Sentencia",
                source=CaseParty.COURT,
                target=CaseParty.PLAINTIFFS,
                type=CaseEventType.SENTENCE,
                simulated=case.simulated,
                procedure_date=procedure_date,
            )
            
            session.add(sentence_event)
            session.commit()
            session.refresh(sentence_event)
            
            logging.info(f">>> ✅ SENTENCE-EVENT: Evento creado exitosamente")
            logging.info(f">>> 📝 SENTENCE: Evento ID: {sentence_event.id}")
            logging.info(f">>> 📝 SENTENCE: Título: {sentence_event.title}")
            logging.info(f">>> 📝 SENTENCE: Tipo: {sentence_event.type}")
            
            return sentence_event
            
        except Exception as e:
            logging.error(f">>> ❌ SENTENCE-EVENT FALLIDO:")
            logging.error(f">>>    Error: {e}")
            logging.error(f">>>    Case: {case.title} (ID: {case.id})")
            session.rollback()
            return None
    
    def _create_trial_start_event(self, session: Session, case: Case, procedure_date: date = None) -> Optional[CaseEvent]:
        """Create trial start event directly without PDF processing."""
        try:
            logging.info(f">>> 🔧 TRIAL_START-EVENT: Iniciando creación...")
            logging.info(f">>> 🆔 Case: {case.title} (ID: {case.id})")
            if procedure_date:
                logging.info(f">>> 📅 Procedure Date: {procedure_date}")
            
            trial_start_event = CaseEvent(
                id=uuid4(),
                case_id=case.id,
                case=case,
                title="Recibe la causa a prueba",
                source=CaseParty.COURT,
                target=CaseParty.PLAINTIFFS,
                type=CaseEventType.TRIAL_START,
                simulated=case.simulated,
                procedure_date=procedure_date,
            )
            
            session.add(trial_start_event)
            session.commit()
            session.refresh(trial_start_event)
            
            logging.info(f">>> ✅ TRIAL_START-EVENT: Evento creado exitosamente")
            logging.info(f">>> 📝 TRIAL_START: Evento ID: {trial_start_event.id}")
            logging.info(f">>> 📝 TRIAL_START: Título: {trial_start_event.title}")
            logging.info(f">>> 📝 TRIAL_START: Tipo: {trial_start_event.type}")
            
            return trial_start_event
            
        except Exception as e:
            logging.error(f">>> ❌ TRIAL_START-EVENT FALLIDO:")
            logging.error(f">>>    Error: {e}")
            logging.error(f">>>    Case: {case.title} (ID: {case.id})")
            session.rollback()
            return None
    
    def _create_notification_event(self, session: Session, case: Case, procedure_date: date = None, description: str = None) -> Optional[CaseEvent]:
        """Create notification event directly without PDF processing."""
        try:
            logging.info(f">>> 🔧 NOTIFICATION-EVENT: Iniciando creación...")
            logging.info(f">>> 🆔 Case: {case.title} (ID: {case.id})")
            if procedure_date:
                logging.info(f">>> 📅 Procedure Date: {procedure_date}")
            if description:
                logging.info(f">>> 📝 Description: {description}")

            event_title = description if description else "Notificación"
            
            notification_event = CaseEvent(
                id=uuid4(),
                case_id=case.id,
                case=case,
                title=event_title,
                source=CaseParty.COURT,
                target=CaseParty.PLAINTIFFS,
                type=CaseEventType.NOTIFICATION,
                simulated=case.simulated,
                procedure_date=procedure_date,
            )
            
            session.add(notification_event)
            session.commit()
            session.refresh(notification_event)
            
            logging.info(f">>> ✅ NOTIFICATION-EVENT: Evento creado exitosamente")
            logging.info(f">>> 📝 NOTIFICATION: Evento ID: {notification_event.id}")
            logging.info(f">>> 📝 NOTIFICATION: Título final: {notification_event.title}")
            logging.info(f">>> 📝 NOTIFICATION: Tipo: {notification_event.type}")
            logging.info(f">>> 📝 NOTIFICATION: Descripción original: {description if description else 'N/A'}")
            logging.info(f">>> 📝 NOTIFICATION: Título procesado: {event_title}")
            
            return notification_event
            
        except Exception as e:
            logging.error(f">>> ❌ NOTIFICATION-EVENT FALLIDO:")
            logging.error(f">>>    Error: {e}")
            logging.error(f">>>    Case: {case.title} (ID: {case.id})")
            session.rollback()
            return None
    
    def _create_translation_evacuation_event(self, session: Session, case: Case, procedure_date: date = None) -> Optional[CaseEvent]:
        """Create translation evacuation event directly without PDF processing."""
        try:
            logging.info(f">>> 🔧 TRANSLATION_EVACUATION-EVENT: Iniciando creación...")
            logging.info(f">>> 🆔 Case: {case.title} (ID: {case.id})")
            if procedure_date:
                logging.info(f">>> 📅 Procedure Date: {procedure_date}")
            
            translation_evacuation_event = CaseEvent(
                id=uuid4(),
                case_id=case.id,
                case=case,
                title="Evacúa traslado",
                source=CaseParty.COURT,
                target=CaseParty.PLAINTIFFS,
                type=CaseEventType.TRANSLATION_EVACUATION,
                simulated=case.simulated,
                procedure_date=procedure_date,
            )
            
            session.add(translation_evacuation_event)
            session.commit()
            session.refresh(translation_evacuation_event)
            
            logging.info(f">>> ✅ TRANSLATION_EVACUATION-EVENT: Evento creado exitosamente")
            logging.info(f">>> 📝 TRANSLATION_EVACUATION: Evento ID: {translation_evacuation_event.id}")
            logging.info(f">>> 📝 TRANSLATION_EVACUATION: Título: {translation_evacuation_event.title}")
            logging.info(f">>> 📝 TRANSLATION_EVACUATION: Tipo: {translation_evacuation_event.type}")
            
            return translation_evacuation_event
            
        except Exception as e:
            logging.error(f">>> ❌ TRANSLATION_EVACUATION-EVENT FALLIDO:")
            logging.error(f">>>    Error: {e}")
            logging.error(f">>>    Case: {case.title} (ID: {case.id})")
            session.rollback()
            return None
    
    def _log_suggestions(self, session: Session, event: CaseEvent) -> None:
        """Log generated suggestions for the event."""
        logging.info(f">>> 🔍 VERIFICANDO SUGERENCIAS para evento {event.id}...")
        
        suggestions_statement = select(CaseEventSuggestion).where(
            CaseEventSuggestion.case_event_id == event.id
        )
        suggestions = session.exec(suggestions_statement).all()
        
        if suggestions:
            logging.info(f">>> ✅ SUGERENCIAS ENCONTRADAS: {len(suggestions)} sugerencias generadas")
            logging.info(f">>> 📋 DETALLE DE SUGERENCIAS:")
            for i, suggestion in enumerate(suggestions, 1):
                logging.info(f">>>    {i}. 📝 {suggestion.name}")
                logging.info(f">>>       🎯 Score: {suggestion.score}")
                logging.info(f">>>       🏷️ Tipo: {suggestion.type.value if suggestion.type else 'N/A'}")
                logging.info(f">>>       🆔 ID: {suggestion.id}")
                if suggestion.content:
                    content_preview = str(suggestion.content)[:100] + "..." if len(str(suggestion.content)) > 100 else str(suggestion.content)
                    logging.info(f">>>       📄 Contenido: {content_preview}")
                logging.info(f">>>       ---")
        else:
            logging.warning(f">>> ⚠️ NO SE GENERARON SUGERENCIAS para evento {event.id}")
            logging.warning(f">>>    Esto puede indicar un problema en la generación de sugerencias")
    
    def _cleanup_pdf_file(self, pdf_path: str, context: str = "procesamiento") -> None:
        """Clean up PDF file after processing."""
        try:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
                logging.info(f">>> 🗑️ PDF eliminado después de {context}: {pdf_path}")
            else:
                logging.warning(f">>> ⚠️ PDF no encontrado para eliminar: {pdf_path}")
        except Exception as cleanup_error:
            logging.error(f">>> ❌ Error al eliminar PDF después de {context}: {cleanup_error}")
    
    async def process_downloaded_pdf(self, pdf_path: str, case_id: str, milestone_type: str, debug: bool = False):
        """Process the downloaded PDF to create event and suggestions based on milestone type."""
        if milestone_type == "hito3":
            logging.info(f">>> 🔄 PROCESANDO PDF PARA DISPATCH-RESOLUTION-EVENT")
            logging.info(f">>> 📋 Flujo: Hito 3 → Dispatch Resolution → Sugerencias")
        else:
            logging.info(f">>> 🔄 PROCESANDO PDF PARA DEMAND-EXCEPTION-EVENT")
            logging.info(f">>> 📋 Flujo: Hito 5 → Demand Exception → Sugerencias")
        
        logging.info(f">>> 📄 Archivo PDF: {pdf_path}")
        logging.info(f">>> 🆔 Case ID: {case_id}")
        logging.info(f">>> 🎯 Tipo de hito: {milestone_type}")
        logging.info(f">>> 🐛 Debug mode: {debug}")
        
        try:
            session = next(get_session())
            logging.info(f">>> 🗄️ Conexión a BD establecida")
            
            try:
                logging.info(f">>> 🔍 PASO 1: Obteniendo caso de la BD...")
                case = self._get_case_by_id(session, case_id)
                if not case:
                    logging.error(f">>> ❌ PASO 1 FALLIDO: No se encontró el caso {case_id}")
                    return
                logging.info(f">>> ✅ PASO 1 EXITOSO: Caso encontrado - {case.title}")
                
                logging.info(f">>> 🔍 PASO 2: Creando evento...")
                # Extraer procedure_date del pdf_info si está disponible
                procedure_date_str = getattr(self, '_current_pdf_info', {}).get('procedure_date')
                procedure_date = parse_procedure_date(procedure_date_str) if procedure_date_str else None
                
                if procedure_date:
                    logging.info(f">>> 📅 Procedure Date extraído: {procedure_date}")
                else:
                    logging.info(f">>> 📅 Procedure Date: No disponible o no válido")
                
                if milestone_type == "hito3":
                    logging.info(f">>> 📝 Creando evento DISPATCH_RESOLUTION...")
                    event = self._create_dispatch_resolution_event(session, case, pdf_path, procedure_date)
                else:
                    logging.info(f">>> 📝 Creando evento DEMAND_EXCEPTION...")
                    event = self._create_demand_exception_event(session, case, pdf_path, procedure_date)
                
                if not event:
                    logging.error(f">>> ❌ PASO 2 FALLIDO: No se pudo crear el evento")
                    return
                logging.info(f">>> ✅ PASO 2 EXITOSO: Evento creado - ID: {event.id}, Tipo: {event.type}")
                
                logging.info(f">>> 🔍 PASO 3: Verificando sugerencias generadas...")
                self._log_suggestions(session, event)

                logging.info(f">>> 🔍 PASO 4: Limpiando archivo PDF...")
                self._cleanup_pdf_file(pdf_path, "procesamiento")
                
                logging.info(f">>> 🎯 PROCESAMIENTO COMPLETADO EXITOSAMENTE")
                logging.info(f">>> 📊 RESUMEN FINAL:")
                logging.info(f">>>    ✅ Evento creado: {event.type} (ID: {event.id})")
                logging.info(f">>>    ✅ PDF procesado: {pdf_path}")
                logging.info(f">>>    ✅ Caso asociado: {case.title} (ID: {case.id})")
                
            finally:
                session.close()
                logging.info(f">>> 🔌 Conexión a BD cerrada")
                
        except Exception as e:
            logging.error(f">>> ❌ ERROR CRÍTICO en procesamiento de PDF:")
            logging.error(f">>>    Error: {e}")
            logging.error(f">>>    PDF: {pdf_path}")
            logging.error(f">>>    Case ID: {case_id}")
            logging.error(f">>>    Milestone: {milestone_type}")
            if debug:
                logging.error(f">>> Traceback completo: {traceback.format_exc()}")
            
            self._cleanup_pdf_file(pdf_path, "error")
