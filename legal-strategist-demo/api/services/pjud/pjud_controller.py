import logging
import re
from datetime import datetime, timedelta

from fastapi import UploadFile
from playwright.async_api import async_playwright, Locator, Page, Request, Response, TimeoutError

from models.api import (
    DemandDeleteRequest,
    DemandDeleteResponse,
    DemandListGetRequest,
    DemandListGetResponse,
    DemandSendRequest,
    DemandSendResponse,
    DemandTextSendRequest,
    DemandTextSendResponse,
    SuggestionRequest,
    SuggestionResponse,
)
from models.pydantic import (
    AnnexFile,
    DemandInformation,
    LegalSubject,
    PJUDABDTE,
    PJUDAddress,
    PJUDAddressType,
    PJUDDDO,
    PJUDDTE,
    PJUDLegalRepresentative,
    SuggestionType,
)
from models.sql import (
    CaseEventSuggestion,
    CourtCase,
)


DEFAULT_WAIT_FOR_TIMEOUT = 3000


class PJUDController:
    def log_requests(self, request: Request) -> None:
        if str(request.url).startswith("https://ojv.pjud.cl/kpitec-ojv-web/rest"):
            logging.info(f"PJUD Request: {request.method} {request.url}")
    
    def log_responses(self, response: Response) -> None:
        if response.status != 200 and response.request.method == "GET":
            logging.info(f"PJUD Response: {response.status} {response.url}")

    async def delete_existing_addresses(self, page: Page) -> None:
        address_cards = page.locator("#listaTemporalDirecciones .pg_card_tr")
        card_count = await address_cards.count()
        if card_count == 0:
            return
    
        for i in range(card_count):
            actions_icon = address_cards.nth(i).locator("a.icon")
            await actions_icon.click()
            try:
                delete_button = page.locator("button:has-text('Borrar Direccion')")
                await delete_button.click()
            except TimeoutError:
                logging.warning("Existing address delete button not found.")

        final_count = await address_cards.count()
        if final_count != 0:
            logging.warning(f"{final_count} addresses remain; deletion may have encountered issues.")

    async def delete_existing_legal_representatives(self, page: Page) -> None:
        rep_cards = page.locator("#listaTemporalRepLegales .pg_card_tr")
        card_count = await rep_cards.count()
        if card_count == 0:
            return
    
        for i in range(card_count):
            actions_icon = rep_cards.nth(i).locator("a.icon")
            await actions_icon.click()
            try:
                delete_button = page.locator("button:has-text('Borrar Representante Legal')")
                await delete_button.click()
            except TimeoutError:
                logging.warning("Existing legal representative delete button not found.")

        final_count = await rep_cards.count()
        if final_count != 0:
            logging.warning(f"{final_count} legal representatives remain; deletion may have encountered issues.")

    async def get_type_of_person(self, page: Page) -> str:
        retries = 5
        for _ in range(retries):
            type_of_person = await page.locator("text='Tipo Persona:'").locator("..").locator("a.select2-choice span.select2-chosen").text_content()
            if type_of_person != "Seleccione Tipo Persona":
                return type_of_person
            await page.wait_for_timeout(500)
        return ""

    async def add_address(self, page: Page, address: PJUDAddress) -> DemandTextSendResponse | None:
        await page.locator("text='Tipo de Direccion'").locator("..").locator("a.select2-choice").click()
        search_box = page.locator("input.select2-input:visible")
        await search_box.fill(address.get_adress_type_label(), force=True)
        await search_box.press("Enter")

        await page.locator("text='Región'").locator("..").locator("a.select2-choice").click()
        search_box = page.locator("input.select2-input:visible")
        await search_box.fill(address.region.value)
        await search_box.press("Enter")

        await page.locator("text='Comuna'").locator("..").locator("a.select2-choice").click()
        search_box = page.locator("input.select2-input:visible")
        await search_box.fill(address.commune.value, force=True)
        await search_box.press("Enter")

        await page.locator("text='Tipo de Calle'").locator("..").locator("a.select2-choice").click()
        search_box = page.locator("input.select2-input:visible")
        await search_box.fill(address.get_street_type_label(), force=True)
        await search_box.press("Enter")

        search_box = page.locator("text='Dirección'").locator("..").locator("input.form-control")
        await search_box.fill(address.address)
        await search_box.press("Enter")
        try:
            await page.locator("text='Dirección'").locator("..").locator("input.form-control.is-valid:visible").wait_for(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
        except TimeoutError:
            logging.warning("Add litigant error: Invalid address.")
            return DemandTextSendResponse(message="Litigante con dirección inválida.", status=400)

        search_box = page.locator("text='Número'").locator("..").locator("input.form-control")
        await search_box.fill(address.address_number)
        await search_box.press("Enter")
        try:
            await page.locator("text='Número'").locator("..").locator("input.form-control.is-valid:visible").wait_for(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
        except TimeoutError:
            logging.warning("Add litigant error: Invalid address number.")
            return DemandTextSendResponse(message="Litigante con número de dirección inválido.", status=400)

        await page.locator("div#botonesDireccion.card button.btn.btn-primary.btn-block:has-text('Ingresar')").nth(0).click()
        try:
            await page.locator("div.toast-message:has-text('Ya hay una Dirección')").wait_for(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
            logging.warning("Add litigant error: Duplicated address type.")
            return DemandTextSendResponse(message="Solo se permite una instancia de cada tipo de dirección para un litigante.", status=400)
        except TimeoutError:
            pass

        return None

    async def add_legal_representative(self, page: Page, legal_representative: PJUDLegalRepresentative) -> DemandTextSendResponse | None:
        if legal_representative.identifier is None:
            logging.warning("Add litigant error: Legal representative without RUT.")
            return DemandTextSendResponse(message="Representante legal sin RUT.", status=400)
        
        search_box = page.locator("text='Rut'").locator("..").locator("input.form-control")
        await search_box.fill(legal_representative.identifier)
        await search_box.press("Enter")
        
        try:
            await page.locator("text='Rut'").locator("..").locator("input.form-control.is-valid:visible").wait_for(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
        except TimeoutError:
            logging.warning("Add litigant error: Legal representative with invalid RUT.")
            return DemandTextSendResponse(message="Representante legal con RUT inválido.", status=400)
        
        await page.locator("div#botonesRepresentanteLegal.card button.btn.btn-primary.btn-block:has-text('Ingresar')").nth(0).click()

        try:
            await page.locator("div.toast-message:has-text('Ya hay un Representante Legal ingresado.')").wait_for(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
            logging.warning("Add litigant error: Litigant already has a legal representative.")
            return DemandTextSendResponse(message="Litigante no puede tener más de un representante legal.", status=400)
        except TimeoutError:
            pass
        
        return None

    async def add_defendant(self, page: Page, defendant: PJUDDDO) -> DemandTextSendResponse | None:
        if defendant.identifier is None:
            logging.warning("Add litigant error: Defendant without RUT.")
            return DemandTextSendResponse(message="Litigante DDO. sin RUT.", status=400)
        
        await page.locator("a.select2-choice.select2-default:has-text('Seleccione Tipo Sujeto')").click()
        search_box = page.locator("input.select2-input:visible")
        await search_box.click(force=True)
        await page.locator("li.select2-result-selectable div.select2-result-label:has-text('DDO.')").nth(0).click(force=True, timeout=DEFAULT_WAIT_FOR_TIMEOUT)

        rut_box = page.locator("input[name='rut'].form-control:visible")
        await rut_box.click()
        await rut_box.fill(defendant.identifier)
        await rut_box.press("Enter")
        try:
            await page.locator("input[name='rut'].form-control.is-valid:visible").wait_for(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
        except TimeoutError:
            logging.warning("Add litigant error: Defendant with invalid RUT.")
            return DemandTextSendResponse(message="Litigante DDO. con RUT inválido.", status=400)
        
        await page.locator("button.btn.btn-info.btn-block:has-text('Datos Litigante')").nth(0).click()
        await page.locator("a.nav-link:has-text('Direcciones')").click()
        await self.delete_existing_addresses(page)
        address_types_considered: list[PJUDAddressType] = []
        for address in defendant.addresses:
            if address.address_type in address_types_considered:
                logging.warning("Add litigant error: Duplicated address type.")
                return DemandTextSendResponse(message="Solo se permite una instancia de cada tipo de dirección para DDO.", status=400)
            response = await self.add_address(page, address)
            if response:
                return response
            address_types_considered.append(address.address_type)

        await page.locator("a.nav-link:has-text('Representantes Legales')").click()
        await self.delete_existing_legal_representatives(page)
        for index, legal_representative in enumerate(defendant.legal_representatives):
            if index > 0:
                break
            response = await self.add_legal_representative(page, legal_representative)
            if response:
                return response
        await page.locator("div.modal-footer button.btn.btn-primary.btn-block:visible:has-text('Guardar')").nth(0).click()

        await page.locator("button.btn.btn-primary.btn-block:has-text('Agregar Litigante')").nth(0).click()       

        try:
            await page.locator("div.toast-message:has-text('Debe ingresar una dirección particular o comercial para este litigante.')").wait_for(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
            logging.warning("Add litigant error: Defendant without address.")
            return DemandTextSendResponse(message="Litigante DDO. sin dirección particular o comercial.", status=400)
        except TimeoutError:
            pass

        return None

    async def add_plaintiff(self, page: Page, plaintiff: PJUDDTE) -> DemandTextSendResponse | None:
        if plaintiff.identifier is None:
            logging.warning("Add litigant error: Plaintiff without RUT.")
            return DemandTextSendResponse(message="Litigante DTE. sin RUT.", status=400)
        
        await page.locator("a.select2-choice.select2-default:has-text('Seleccione Tipo Sujeto')").click(force=True)
        search_box = page.locator("input.select2-input:visible")
        await search_box.click(force=True)
        await page.locator("li.select2-result-selectable div.select2-result-label:has-text('DTE.')").nth(0).click(force=True, timeout=DEFAULT_WAIT_FOR_TIMEOUT)

        rut_box = page.locator("input[name='rut'].form-control:visible")
        await rut_box.click()
        await rut_box.fill(plaintiff.identifier)
        await rut_box.press("Enter")
        try:
            await page.locator("input[name='rut'].form-control.is-valid:visible").wait_for(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
        except TimeoutError:
            logging.warning("Add litigant error: Plaintiff with invalid RUT.")
            return DemandTextSendResponse(message="Litigante DTE. con RUT inválido.", status=400)
        
        type_of_person = await self.get_type_of_person(page)
        if type_of_person != "JURIDICA":
            logging.warning("Add litigant error: Plaintiff is not a legal person.")
            return DemandTextSendResponse(message="Litigante DTE. no es una persona juriídica.", status=400)

        await page.locator("button.btn.btn-info.btn-block:has-text('Datos Litigante')").nth(0).click()
        await page.locator("a.nav-link:has-text('Representantes Legales')").click()
        await self.delete_existing_legal_representatives(page)
        for index, legal_representative in enumerate(plaintiff.legal_representatives):
            if index > 0:
                break
            response = await self.add_legal_representative(page, legal_representative)
            if response:
                return response
        await page.locator("div.modal-footer button.btn.btn-primary.btn-block:visible:has-text('Guardar')").nth(0).click()

        await page.locator("button.btn.btn-primary.btn-block:has-text('Agregar Litigante')").nth(0).click()

        try:
            await page.locator("div.toast-message:has-text('Debe ingresar una dirección particular o comercial para este litigante.')").wait_for(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
            logging.warning("Add litigant error: Plaintiff without address.")
            return DemandTextSendResponse(message="Litigante DTE. sin dirección particular o comercial.", status=400)
        except TimeoutError:
            pass

        try:
            await page.locator("div.toast-message:has-text('Por favor, ingrese datos del Representante Legal para el Litigante, si los conoce.')").wait_for(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
            logging.warning("Add litigant error: Plaintiff without legal representatives.")
            return DemandTextSendResponse(message="Litigante DTE. sin representantes legales.", status=400)
        except TimeoutError:
            pass

        return None

    async def add_sponsoring_attorney(self, page: Page, attorney: PJUDABDTE) -> DemandTextSendResponse | None:
        if attorney.identifier is None:
            logging.warning("Add litigant error: Sponsoring attorney without RUT.")
            return DemandTextSendResponse(message="Litigante AB.DTE sin RUT.", status=400)
        
        await page.locator("a.select2-choice.select2-default:has-text('Seleccione Tipo Sujeto')").click()
        search_box = page.locator("input.select2-input:visible")
        await search_box.click(force=True)
        await page.locator("li.select2-result-selectable div.select2-result-label:has-text('AB.DTE.')").click(force=True, timeout=DEFAULT_WAIT_FOR_TIMEOUT)

        rut_box = page.locator("input[name='rut'].form-control:visible")
        await rut_box.click()
        await rut_box.fill(attorney.identifier)
        await rut_box.press("Enter")
        try:
            await page.locator("input[name='rut'].form-control.is-valid:visible").wait_for(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
        except TimeoutError:
            logging.warning("Add litigant error: Sponsoring attorney with invalid RUT.")
            return DemandTextSendResponse(message="Litigante AB.DTE. con RUT inválido.", status=400)

        await page.locator("button.btn.btn-primary.btn-block:has-text('Agregar Litigante')").nth(0).click()

        try:
            await page.locator("div.toast-message:has-text('El abogado no es valido')").wait_for(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
            logging.warning("Add litigant error: Invalid attorney.")
            return DemandTextSendResponse(message="Litigante AB.DTE. no es un abogado válido.", status=400)
        except TimeoutError:
            pass

        return None

    async def connect_to_pjud(self, page: Page, password: str, rut: str) -> str | None:
        page.on("console", lambda msg: logging.info(f"PJUD console: {msg.text}"))
        #page.on("request", self.log_requests)
        #page.on("requestfailed", lambda request: logging.info(f"Request failed: {request.url} {request.failure}"))
        page.on("response", self.log_responses)

        await page.goto("https://ojv.pjud.cl/kpitec-ojv-web/views/login.html#segunda")

        try:
            await page.locator("#modalAviso:visible").nth(0).wait_for(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
            await page.locator("#modalAviso div.i-close:visible").nth(0).click()
        except TimeoutError:
            pass

        await page.locator("#inputRut2C").fill(rut.split("-")[0])
        await page.locator("#inputPassword2C").fill(password)
        await page.locator("button[type='submit']:has-text('Ingresar')").nth(0).click()

        try:
            await page.locator("text=¡Error de Autenticación! Usuario o contraseña Invalido.").nth(0).wait_for(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
            logging.warning("Authentication failed: Invalid username or password.")
            return "Credenciales PJUD incorrectas."
        except TimeoutError:
            pass

        try:
            await page.locator("body:has-text('Error 500')").wait_for(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
            logging.warning("PJUD server error.")
            return "PJUD no se encuentra disponible en este momento, vuelva a intentar más tarde."
        except TimeoutError:
            pass
    
    async def connect_to_demand_list(self, page: Page) -> None:
        await page.locator("div.list-group-item.list-group-item-action.p-2.pg_menu_lt:has-text('Bandeja Demandas/Recursos')").wait_for()
        await page.locator("div.list-group-item.list-group-item-action.p-2.pg_menu_lt:has-text('Bandeja Demandas/Recursos')").click()

        competencia_select = page.locator("div.form-group:has(label:text-is('Competencia:')) select.form-control")
        await competencia_select.wait_for()
        await competencia_select.select_option(label="Civil")

        start_date = (datetime.now() - timedelta(days=21)).strftime("%d/%m/%Y")
        date_input = page.locator("text='Fecha Desde'").locator("..").locator("div.input-group.date input.form-control.datetimepicker-input")
        await date_input.fill(start_date)

        await page.locator("input.btn.btn-primary.btn-block[value='Consultar Demandas']").click()
        await page.wait_for_timeout(DEFAULT_WAIT_FOR_TIMEOUT)

    async def extract_demand_information(self, card_locator: Locator, index: int) -> DemandInformation | None:
        try:
            raw_date = await card_locator.locator(".card-text[data-bind*='fechaCortaIngresoComp']").text_content()
            creation_date_iso = datetime.strptime(raw_date, "%d/%m/%y").isoformat()

            demand_information = DemandInformation(
                title=await card_locator.locator(".card-text[data-bind*='cuaderno().parte']").text_content(),
                creation_date=creation_date_iso,
                court=await card_locator.locator(".card-text[data-bind*='tribunal().nombre']").text_content(),
                legal_subject=await card_locator.locator(".card-text[data-bind*='materias()']").text_content(),
                author=await card_locator.locator(".card-text[data-bind*='responsable().nombres']").text_content(),
                index=index,
            )
            demand_information.title = demand_information.title.strip()
            return demand_information
        except Exception as e:
            logging.warning(f"Error extracting information from a demand card: {e}")
            return None

    async def get_demand_list_from_pjud(self, request: DemandListGetRequest) -> DemandListGetResponse:
        demand_list: list[DemandInformation] = []

        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                response = await self.connect_to_pjud(page, request.password, request.rut)
                if response:
                    return DemandListGetResponse(message=response, status=401)
                
                await self.connect_to_demand_list(page)

                cards = page.locator("div.card.pg_card_tr")
                num_cards = await cards.count()
                for i in range(num_cards):
                    card = cards.nth(i)
                    card_info = await self.extract_demand_information(card, i)
                    demand_list.append(card_info)
                
                await browser.close()
            
            return DemandListGetResponse(message="Valid", status=200, data=demand_list)
        except Exception as e:
            logging.error("Failed to get demands from PJUD: %s", e)
            raise
    
    async def delete_demand(self, request: DemandDeleteRequest) -> DemandDeleteResponse:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                response = await self.connect_to_pjud(page, request.password, request.rut)
                if response:
                    return DemandSendResponse(message=response, status=401)
                
                await self.connect_to_demand_list(page)

                cards = page.locator("div.card.pg_card_tr")
                num_cards = await cards.count()
                for i in range(num_cards):
                    if i != request.index:
                        continue
                    card = cards.nth(i)
                    await card.locator("a.icon").click()
                    await page.locator("button.btn-danger.btn-sm.text-left.w-100:has-text('Eliminar Causa'):visible").click()

                    modal = page.locator("#modalConfirmarEliminar2")
                    await modal.wait_for(state="visible", timeout=DEFAULT_WAIT_FOR_TIMEOUT)
                    await modal.locator("button.btn.btn-primary").click()
                    break
                else:
                    logging.warning("Failed to find demand")
                    return DemandSendResponse(message=f"Could not find demand with index {request.index}", status=400)
                
                await browser.close()
                
            return DemandDeleteResponse(message="Valid", status=200)
        except Exception as e:
            logging.error("Failed to delete demand: %s", e)
            raise

    async def send_demand_to_court(self, request: DemandSendRequest) ->  DemandSendResponse:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                response = await self.connect_to_pjud(page, request.password, request.rut)
                if response:
                    return DemandSendResponse(message=response, status=401)
                
                await self.connect_to_demand_list(page)

                cards = page.locator("div.card.pg_card_tr")
                num_cards = await cards.count()
                for i in range(num_cards):
                    if i != request.index:
                        continue
                    checkbox = cards.nth(i).locator("label[for^='idCheckSelCau-']")
                    if not await checkbox.is_checked():
                        await checkbox.check()
                    await page.locator("input.btn-warning[value='Enviar Poder Judicial']").wait_for(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
                    # TODO: Click the button
                    break
                else:
                    logging.warning("Failed to find demand")
                    return DemandSendResponse(message=f"Could not find demand with index {request.index}", status=400)
                
                await browser.close()
                
            return DemandSendResponse(message="Valid", status=200)
        except Exception as e:
            logging.error("Failed to send demand to court: %s", e)
            raise

    async def send_demand_to_pjud(self, request: DemandTextSendRequest, demand_text: UploadFile, annexes: list[AnnexFile]) -> DemandTextSendResponse:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                response = await self.connect_to_pjud(page, request.password, request.rut)
                if response:
                    return DemandTextSendResponse(message=response, status=401)

                send_demand_selector = "div.list-group-item.list-group-item-action.p-2.pg_menu_lt:has-text('Ingresar Demanda/Recurso')"
                await page.locator(send_demand_selector).wait_for()
                await page.locator(send_demand_selector).click()

                competencia_select = page.locator("div.form-group:has(label:text-is('Competencia')) select.form-control")
                await competencia_select.wait_for()
                await competencia_select.select_option(label="Familia")
                await competencia_select.wait_for()
                await competencia_select.select_option(label="Laboral")
                await competencia_select.wait_for()
                await competencia_select.select_option(label="Civil")
                await competencia_select.wait_for()
                await competencia_select.select_option(label="Civil")

                #TODO: Use PJUDRegion get_court_label
                await page.locator("div#s2id_select-asientoCorte a.select2-choice").click()
                await page.locator("li.select2-result-selectable div.select2-result-label:has-text('C.A. de Santiago')").click(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
                await page.locator("div#s2id_select-asientoCorte a.select2-choice").click()
                await page.locator("li.select2-result-selectable div.select2-result-label:has-text('C.A. de San Miguel')").click(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
                await page.locator("div#s2id_select-asientoCorte a.select2-choice").click()
                await page.locator("li.select2-result-selectable div.select2-result-label:has-text('C.A. de Santiago')").click(timeout=DEFAULT_WAIT_FOR_TIMEOUT)

                #TODO: Use PJUDRegion get_tribunal_label
                await page.locator("div#s2id_select-tribunales a.select2-choice").click()
                await page.locator("li.select2-result-selectable div.select2-result-label:has-text('Dist. Corte Santiago')").click()

                await page.locator("a.select2-choice.select2-default:has-text('Seleccione Procedimiento')").click()
                search_box = page.locator("input.select2-input:visible")
                await search_box.click()
                await search_box.fill("Ejecutivo")
                await search_box.press("Enter")

                await page.locator("a.select2-choice.select2-default:has-text('Seleccione Materia')").click()
                search_box = page.locator("input.select2-input:visible")
                await search_box.click(force=True)
                if request.legal_subject == LegalSubject.PROMISSORY_NOTE_COLLECTION:
                    await search_box.fill("Pagaré, Cobro De", force=True)
                elif request.legal_subject == LegalSubject.BILL_COLLECTION:
                    await search_box.fill("Factura, Cobro De", force=True)
                else:
                    await search_box.fill("Obligación De Dar, Cumplimiento", force=True)
                await search_box.press("Enter")

                await page.locator("button.btn.btn-primary.btn-block:has-text('Agregar')").nth(0).click()
                await page.mouse.wheel(0, 500)

                # Add sponsoring attorneys
                for attorney in request.sponsoring_attorneys:
                    response = await self.add_sponsoring_attorney(page, attorney)
                    if response:
                        return response

                # Add defendants
                for defendant in list(reversed(request.defendants)):
                    response = await self.add_defendant(page, defendant)
                    if response:
                        return response

                # Add plaintiffs
                for plaintiff in request.plaintiffs:
                    response = await self.add_plaintiff(page, plaintiff)
                    if response:
                        return response
                
                await page.locator("button.btn.btn-primary.btn-block:visible:has-text('Ingresar')").nth(0).click()

                demand_text_data = {
                    "name": demand_text.filename,
                    "mimeType": demand_text.content_type,
                    "buffer": await demand_text.read(),
                }

                try:
                    async with page.expect_file_chooser() as fc_info:
                        await page.locator("div#dDPrincipal button.btn.btn-primary.btn-block:visible:has-text('Adjuntar')").nth(0).click()
                        file_chooser = await fc_info.value
                        await file_chooser.set_files(demand_text_data)
                except Exception as e:
                    logging.error(f"Could not upload demand text file: {e}")
                
                for annex in annexes:
                    label_box = page.locator("div#dDAnexo input[placeholder='Documento']:visible")
                    await label_box.click()
                    await label_box.fill(annex.label)

                    annex_data = {
                        "name": annex.upload_file.filename,
                        "mimeType": annex.upload_file.content_type,
                        "buffer": await annex.upload_file.read(),
                    }

                    try:
                        async with page.expect_file_chooser() as fc_info:
                            await page.locator("div#dDAnexo button.btn.btn-primary.btn-block:visible:has-text('Adjuntar')").nth(0).click()
                            file_chooser = await fc_info.value
                            await file_chooser.set_files(annex_data)
                    except Exception as e:
                        logging.error(f"Could not upload {annex.label} file: {e}")

                await page.locator("div#modalMultiArchivos button.btn.btn-primary.btn-block:visible:has-text('Cerrar y Continuar')").nth(0).click()

                await browser.close()

            return DemandTextSendResponse(message="Valid", status=200)
        except Exception as e:
            logging.error("Failed to send demand to PJUD: %s", e)
            raise

    async def send_suggestion_to_pjud(self, request: SuggestionRequest, court_case: CourtCase, suggestion: CaseEventSuggestion, suggestion_file: UploadFile) -> SuggestionResponse:
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page()
                response = await self.connect_to_pjud(page, request.password, request.rut)
                if response:
                    return SuggestionResponse(message=response, status=401)
                
                send_document_selector = "div.list-group-item.list-group-item-action.p-2.pg_menu_lt:has-text('Ingresar Escrito')"
                await page.locator(send_document_selector).wait_for()
                await page.locator(send_document_selector).click()

                competencia_selector = "div#s2id_autogen1 a.select2-choice:visible"
                competencia_value_selector = "li.select2-result-selectable div.select2-result-label:has-text('Civil')"
                competencia_value_dummy_selector = "li.select2-result-selectable div.select2-result-label:has-text('Corte Suprema')"
                await page.locator(competencia_selector).click()
                await page.locator(competencia_value_selector).click(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
                await page.locator(competencia_selector).click()
                await page.locator(competencia_value_dummy_selector).click(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
                await page.locator(competencia_selector).click()
                await page.locator(competencia_value_selector).click(timeout=DEFAULT_WAIT_FOR_TIMEOUT)

                court_label = court_case.get_court_label()
                if not court_label:
                    return SuggestionResponse(message="Could not map court and case data to PJUD available selection", status=500)
                
                court_selector = "div#s2id_select2-tribunales a.select2-choice:visible"
                await page.locator(court_selector).click()
                await page.locator("div#select2-drop div.select2-search input.select2-input:visible").fill(court_label)
                await page.locator("li.select2-result-selectable").get_by_role("option", name=court_label, exact=True).locator("span").click(timeout=DEFAULT_WAIT_FOR_TIMEOUT)

                type_select = page.locator("div.row div.form-group:has(label:text-is('Tipo')) select.form-control")
                await type_select.wait_for()
                await type_select.select_option(label="C")

                pattern = r"C-(\d+)-(\d{4})"
                match = re.search(pattern, court_case.role)
                if not match:
                    return SuggestionResponse(message="Could not get case numeric role", status=500)
                role = int(match.group(1))
                year = int(match.group(2))

                role_box = page.locator("div.row div.form-group:has(label:text-is('Rol')) input.form-control:visible")
                await role_box.click()
                await role_box.fill(str(role))
                await role_box.press("Enter")

                type_select = page.locator("div.row div.form-group:has(label:text-is('Año')) select.form-control")
                await type_select.wait_for()
                await type_select.select_option(label=str(year))

                search_box = page.locator('div.row button[data-bind*="loadCausa"]:visible')
                await search_box.click()

                await page.locator("div.row div.form-group:has(label:text-is('Cuaderno')) a.select2-choice:visible").click()
                await page.locator("div#select2-drop div.select2-search input.select2-input:visible").fill("1 ")
                await page.locator("li.select2-result-selectable").get_by_role("option", name="1 ").locator("span").click(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
            
                try:
                    await page.locator("div.toast-message:has-text('se encuentra Archivada.')").wait_for(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
                    logging.warning("Send suggestion error: Demand is archived.")
                    return DemandTextSendResponse(message="El caso se encuentra archivado.", status=400)
                except TimeoutError:
                    pass

                await page.locator("div.row div.form-group:has(label:text-is('Parte que Presenta')) a.select2-choice:visible").click(force=True)
                part_box = page.locator("div#select2-drop div.select2-search input.select2-input:visible")
                await part_box.fill("AB.DTE", force=True)
                await page.locator("li.select2-result-selectable").get_by_role("option", name="AB.DTE").locator("span").nth(0).click(timeout=DEFAULT_WAIT_FOR_TIMEOUT, force=True)
                await page.mouse.wheel(0, 500)

                await page.locator("div.row div.form-group:has(label:text-is('Grupo Escrito')) a.select2-choice:visible").click(force=True)
                document_group_box = page.locator("div#select2-drop div.select2-search input.select2-input:visible")
                await document_group_box.fill("Escritos Generales", force=True)
                await page.locator("li.select2-result-selectable").get_by_role("option", name="Escritos Generales").locator("span").nth(0).click(timeout=DEFAULT_WAIT_FOR_TIMEOUT, force=True)

                await page.screenshot(path="full_page_screenshot.png", full_page=True)

                document_type = "Contesta oficio"
                if suggestion.type == SuggestionType.DEMAND_TEXT_CORRECTION:
                    document_type = "Rectifica demanda"
                elif suggestion.type == SuggestionType.COMPROMISE:
                    document_type = "Avenimiento/transacción"
                elif suggestion.type == SuggestionType.EXCEPTIONS_RESPONSE:
                    document_type = "Evacúa traslado"
                elif suggestion.type == SuggestionType.RESPONSE:
                    document_type = "Cumple lo ordenado"
                elif suggestion.type == SuggestionType.REQUEST:
                    document_type = "Se oficie"
                await page.locator("div.row div.form-group:has(label:text-is('Tipo Escrito')) a.select2-choice:visible").click(force=True)
                document_box = page.locator("div#select2-drop div.select2-search input.select2-input:visible")
                await document_box.fill(document_type, force=True)
                await page.locator("li.select2-result-selectable").get_by_role("option", name=document_type).locator("span").nth(0).click(timeout=DEFAULT_WAIT_FOR_TIMEOUT, force=True)

                await page.locator("button.btn.btn-primary.btn-block:visible:has-text('Grabar Escrito')").nth(0).click()

                suggestion_data = {
                    "name": suggestion_file.filename,
                    "mimeType": suggestion_file.content_type,
                    "buffer": await suggestion_file.read(),
                }

                try:
                    async with page.expect_file_chooser() as fc_info:
                        await page.locator("div#dDPrincipal button.btn.btn-primary.btn-block:visible:has-text('Adjuntar')").nth(0).click()
                        file_chooser = await fc_info.value
                        await file_chooser.set_files(suggestion_data)
                except Exception as e:
                    logging.error(f"Could not upload suggestion file: {e}")

                await page.locator("div#modalMultiArchivos button.btn.btn-primary.btn-block:visible:has-text('Cerrar y Continuar')").nth(0).click()
                
                await browser.close()
                
            return SuggestionResponse(message="Valid", status=200)
        except Exception as e:
            logging.error("Failed to send suggestion to court: %s", e)
            raise
