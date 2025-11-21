import logging
from typing import Any

from playwright.async_api import async_playwright, Frame, Locator, Page, TimeoutError
from twocaptcha import TwoCaptcha
from urllib.parse import urlparse, parse_qs

from config import Config
from models.api import DigitalCuratorsRequest, DigitalCuratorsResponse
from models.pydantic import DigitalCuratorsItem


DEFAULT_WAIT_FOR_TIMEOUT = 3000


class DigitalCuratorsScrapper:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.solver = TwoCaptcha(Config.TWO_CAPTCHA_KEY)

    async def connect_to_website(self, page: Page) -> str | None:
        #page.on("console", lambda msg: logging.info(f"Digital curators console: {msg.text}"))
        await page.goto("https://conservadoresdigitales.cl/conservador/santiago/consultas-en-linea/indice-de-propiedad")
        
    async def extract_information(self, request: DigitalCuratorsRequest) -> DigitalCuratorsResponse:
        response_items: list[DigitalCuratorsItem] = []
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=self.headless)
                page = await browser.new_page()
                response = await self.connect_to_website(page)
                if response:
                    return DigitalCuratorsResponse(message=response, status=401)
                
                await page.locator("md-tab-item:has-text('Por Nombre o Dirección')").click()
                await page.wait_for_selector('input[name="nombre"]', state="visible")
                input_field = page.locator('input[name="nombre"]')
                await input_field.click()
                await input_field.fill(request.name)

                iframe_element = page.locator("iframe[title='reCAPTCHA']").nth(1)
                iframe_name = await iframe_element.get_attribute("name")
                if not iframe_name:
                    logging.warning("reCAPTCHA iFrame not found")
                    return DigitalCuratorsResponse(message="reCAPTCHA iFrame not found", status=500)

                captcha_frame = page.frame(name=iframe_name)
                captcha_url = captcha_frame.url
                #page_url = page.url
                query_params = parse_qs(urlparse(captcha_url).query)
                site_key = query_params.get("k", [None])[0]
                if not site_key:
                    logging.warning("reCAPTCHA site key not found")
                    return DigitalCuratorsResponse(message="reCAPTCHA site key not found", status=500)
                captcha_solution = "true"#self._solve_captcha(site_key, page_url)

                if captcha_solution:
                    #await page.evaluate(f"""
                    #    const textarea = document.querySelector('textarea[id="g-recaptcha-response-1"]');
                    #    textarea.value = '{captcha_solution}';
                    #    textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
                    #""")
                    await captcha_frame.locator("#recaptcha-anchor").click()

                    try:
                        await page.wait_for_function("""
                            () => document.querySelector('#recaptcha-anchor[aria-checked="true"]') || 
                                document.querySelector("iframe[src*='google.com/recaptcha/api2/bframe']")
                        """, timeout=DEFAULT_WAIT_FOR_TIMEOUT)
                        for _ in range(3):
                            image_recaptcha = None
                            try:
                                await page.locator("iframe[src*='google.com/recaptcha/api2/bframe']:visible").wait_for()
                                image_recaptcha = page.locator("iframe[src*='google.com/recaptcha/api2/bframe']:visible")
                            except TimeoutError as e:
                                pass
                            if image_recaptcha:
                                logging.info("Image challenge detected")
                                expired = await self._solve_image_challenge(page, captcha_frame, image_recaptcha)
                                if not expired:
                                    break
                            else:
                                logging.info("No image challenge detected")
                                break
                        else:
                            logging.warning("Multiple expired challenges")
                    except TimeoutError:
                        logging.warning("Challenge state not resolved")
                        raise ValueError("reCAPTCHA answer failed")

                    try:
                        await captcha_frame.locator("#recaptcha-anchor[aria-checked='true']").wait_for(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
                    except TimeoutError:
                        logging.warning("reCAPTCHA answer failed")
                        raise ValueError("reCAPTCHA answer failed")
                else:
                    logging.warning("reCAPTCHA solving failed")
                    return DigitalCuratorsResponse(message="reCAPTCHA solving failed", status=500)
                
                try:
                    await page.locator("div#div4 button[type='submit']").click()
                except TimeoutError:
                    logging.warning("Post reCAPTCHA button not available")
                    return DigitalCuratorsResponse(message="Post reCAPTCHA button not available", status=500)

                try:
                    await page.locator("body:has-text('No se ha logrado verificar la consulta correctamente')").wait_for(timeout=DEFAULT_WAIT_FOR_TIMEOUT)
                    logging.warning("Website query unavailable at this moment")
                    return DigitalCuratorsResponse(message="Website query unavailable at this moment", status=500)
                except TimeoutError:
                    pass

                items = page.locator("table.mdl-data-table.md-whiteframe-z1.table-responsive tbody tr")
                num_items = await items.count()
                for i in range(num_items):
                    item = items.nth(i)
                    item_info = await self._extract_item_information(item)
                    if item_info:
                        response_items.append(item_info)

                await browser.close()
                return DigitalCuratorsResponse(message="Success", status=200, data=response_items)
        except Exception as e:
            logging.error(f"Failed to extract information: {e}")
            raise e
    
    async def _extract_item_information(self, item_locator: Locator) -> DigitalCuratorsItem | None:
        try:
            item_information = DigitalCuratorsItem(
                folio=await item_locator.locator("td[data-label*='Foja']").text_content(timeout=DEFAULT_WAIT_FOR_TIMEOUT),
                number=await item_locator.locator("td[data-label*='Número']").text_content(timeout=DEFAULT_WAIT_FOR_TIMEOUT),
                year=await item_locator.locator("td[data-label*='Año']").text_content(timeout=DEFAULT_WAIT_FOR_TIMEOUT),
                name=await item_locator.locator("td[data-label*='Nombre']").text_content(timeout=DEFAULT_WAIT_FOR_TIMEOUT),
                address=await item_locator.locator("td[data-label*='Dirección']").text_content(timeout=DEFAULT_WAIT_FOR_TIMEOUT),
                event=await item_locator.locator("td[data-label*='Acto']").text_content(timeout=DEFAULT_WAIT_FOR_TIMEOUT),
            )
            return item_information
        except Exception as e:
            logging.warning(f"Error extracting information from item: {e}")
            return None
    
    async def _handle_error_messages(self, image_frame: Frame) -> bool:
        if await image_frame.locator(".rc-imageselect-incorrect-response").is_visible(timeout=DEFAULT_WAIT_FOR_TIMEOUT):
            logging.info(f"Incorrect error: {await image_frame.locator('.rc-imageselect-incorrect-response').inner_text()}")
            return True
        elif await image_frame.locator(".rc-imageselect-error-select-more").is_visible(timeout=DEFAULT_WAIT_FOR_TIMEOUT):
            logging.info(f"Select more error: {await image_frame.locator('.rc-imageselect-error-select-more').inner_text()}")
            return True
        elif await image_frame.locator(".rc-imageselect-error-dynamic-more").is_visible(timeout=DEFAULT_WAIT_FOR_TIMEOUT):
            logging.info(f"Dynamic more error: {await image_frame.locator('.rc-imageselect-error-dynamic-more').inner_text()}")
            return True
        elif await image_frame.locator(".rc-imageselect-error-select-something").is_visible(timeout=DEFAULT_WAIT_FOR_TIMEOUT):
            logging.info(f"Select something error: {await image_frame.locator('.rc-imageselect-error-select-something').inner_text()}")
            return True
        return False

    def _parse_numbers(self, content: str) -> list[str]:
        numbers_str = content.split(":")[1]
        number_list = list(map(int, numbers_str.split("/")))
        return number_list
    
    async def _solve_image_challenge(self, page: Page, captcha_frame: Frame, image_recaptcha: Locator) -> bool | None:
        image_frame = page.frame(name=await image_recaptcha.get_attribute("name"))
        with open("services/scrapper/get_captcha_data.js", "r") as f:
            script_get_data_captcha = f.read()
        with open("services/scrapper/track_image_updates.js", "r") as f:
            script_change_tracking = f.read()
        await image_frame.evaluate(f"""
            {script_get_data_captcha}
            {script_change_tracking}
        """)

        id = None

        while True:
            captcha_data = await image_frame.evaluate("""
                getCaptchaData();
            """)

            params = {
                "method": "base64",
                "img_type": "recaptcha",
                "recaptcha": 1,
                "cols": captcha_data["columns"],
                "rows": captcha_data["rows"],
                "textinstructions": captcha_data["comment"],
                "lang": "es",
                "can_no_answer": 1,
            }
            if params["cols"] == 3 and id:
                params["previousID"] = id

            result = self._solve_grid(file=captcha_data["body"], **params)
            if result is None:
                logging.warning("reCAPTCHA image challenge failed")
                raise ValueError("reCAPTCHA image challenge failed")
            
            if await captcha_frame.locator("#rc-anchor-error-msg").is_visible(timeout=DEFAULT_WAIT_FOR_TIMEOUT):
                logging.info("Challenge expired")
                return True
            
            if result and "No_matching_images" not in result["code"]:
                if id is None and params["cols"] == 3 and result["captchaId"]:
                    id = result["captchaId"]
                
                answer = result["code"]
                number_list = self._parse_numbers(answer)
                logging.info(f"Image challenge solved with solution: {number_list}")

                if params["cols"] == 3:
                    image_update = False
                    for index in number_list:
                        grid_cell = image_frame.locator(f"td[tabindex='{index + 3}']")
                        await grid_cell.click()

                    image_update = await image_frame.evaluate("""
                        monitorRequests();
                    """)
                    if image_update:
                        logging.info(f"Images updated, continuing with previousID: {id}")
                        continue
                    await image_frame.locator("#recaptcha-verify-button").click()

                elif params["cols"] == 4:
                    for index in number_list:
                        grid_cell = image_frame.locator(f"td[tabindex='{index + 3}']")
                        await grid_cell.click()
                        #await image_frame.wait_for_timeout(DEFAULT_WAIT_FOR_TIMEOUT)

                    await image_frame.locator("#recaptcha-verify-button").click()
                    image_update = await image_frame.evaluate("""
                        monitorRequests();
                    """)
                    if image_update:
                        logging.info("Images updated, continuing without previousID")
                        continue
                
                if await self._handle_error_messages(image_frame):
                    continue
                break
            elif "No_matching_images" in result["code"]:
                logging.info("No matching images")
                await image_frame.locator("#recaptcha-verify-button").click()
                if await self._handle_error_messages(image_frame):
                    continue
                break

    def _solve_captcha(self, site_key: str, page_url: str) -> str | None:
        try:
            result = self.solver.recaptcha(sitekey=site_key, url=page_url)
            return result["code"]
        except Exception as e:
            logging.warning(f"Error solving CAPTCHA: {e}")
            return None
    
    def _solve_grid(self, file: str, **params) -> dict[str, str | Any] | None:
        try:
            result = self.solver.grid(file=file, **params)
            return result
        except Exception as e:
            logging.warning(f"Error solving grid: {e}")
            return None
