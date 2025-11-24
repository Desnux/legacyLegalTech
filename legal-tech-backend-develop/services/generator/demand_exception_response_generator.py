import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pydantic import BaseModel, Field

from models.pydantic import (
    JudicialCollectionDemandExceptionRequest,
    LegalException,
    LegalExceptionRequest,
    LegalExceptionResponse,
    LegalExceptionResponseInput,
    LegalExceptionResponseRequest,
    Locale,
)
from services.v2.document.demand_exception import DemandExceptionInformation
from services.v2.document.demand_text import DemandTextStructure
from util import int_to_ordinal
from .base_generator import BaseGenerator


class AdditionalRequests(BaseModel):
    requests: list[LegalExceptionResponseRequest] | None = Field(None, description="Additional requests to include in the response, if any")


class Response(BaseModel):
    text: str | None = Field(None, description="Generation output")


class DemandExceptionResponseGenerator(BaseGenerator):
    def __init__(self, input: LegalExceptionResponseInput, locale: Locale = Locale.ES_ES) -> None:
        self.input = input
        self.generator_llm = self.get_structured_generator(Response)
        self.requests_llm = self.get_structured_generator(AdditionalRequests)
        self.locale = locale
    
    def generate(self, demand_exception: DemandExceptionInformation, demand_text: DemandTextStructure) -> LegalExceptionResponse:
        demand_text_content = demand_text.model_dump_json(include={"opening", "missing_payment_arguments", "main_request", "additional_requests"})
        court = self._generate_court()
        opening = self._generate_opening()
        exception_responses = self._generate_exception_responses(demand_exception.exceptions or [], demand_text_content)
        main_request = self._generate_main_request()

        if self.input.suggestion and self.input.secondary_requests is None:
            try:
                self._self_generate_additional_requests(opening)
            except Exception as e:
                logging.warning(f"Could not self generate additional requests for demand exception response: {e}")

        summary = self._generate_summary()
        additional_requests = self._generate_additional_requests()

        return LegalExceptionResponse(
            summary=summary,
            court=court,
            opening=opening,
            exception_responses=exception_responses,
            main_request=main_request,
            additional_requests=additional_requests,
        )
    
    def _generate_summary(self) -> str | None:
        segments: list[str] = []
        secondary_segments: list[str] = []
        affix = "OTROSÍ"
        segments.append("EN LO PRINCIPAL: EVACUA TRASLADO")

        for secondary_request in self.input.secondary_requests or []:
            if secondary_request.nature:
                if secondary_request.nature == LegalExceptionRequest.OTHER and secondary_request.context:
                    prompt = f"Generate a brief and formal legal sentence in {self.locale} that summarizes a request or obligation using an impersonal tone in less than 8 words."
                    prompt += f"\nFor context of the request or obligation, consider: <context>{secondary_request.context}</context>"
                    prompt += "\nDo not add quotation marks or special symbols"
                    try:
                        request: Response = self.generator_llm.invoke(prompt)
                    except Exception as e:
                        logging.warning(f"Could not generate additional request summary: {e}")
                        continue
                    if request and request.text:
                        secondary_segments.append(request.text.upper().replace("\"", "").replace(".", "").strip())
                else:
                    secondary_segments.append(secondary_request.nature.to_localized_string(self.locale))
        if len(secondary_segments) > 0:
            numbered_segments = [f"{int_to_ordinal(i + 1, self.locale)} {affix}: {segment}" for i, segment in enumerate(secondary_segments)]
            segments.extend(numbered_segments)
        if len(segments) == 0:
            return None
        return "; ".join(segments)

    def _generate_court(self) -> str:
        if self.input.court_city and self.input.court_number:
            return f"S.J.L. CIVIL DE {self.input.court_city.upper()} ({self.input.court_number}º)"
        if self.input.court_city:
            return f"S.J.L. CIVIL DE {self.input.court_city.upper()}"
        return "S.J.L."
    
    def _generate_opening(self) -> str:
        template = """
        {sponsoring_attorney.name}, abogado, por el ejecutante, {plaintiff.name}, en los autos caratulados “{case_title}”, ROL {case_role}, a US., con respeto digo:

        Que por este acto, y estando dentro de plazo, vengo en evacuar traslado conferido con {request_date (format_example: 12 de octubre de 2021)},
        respecto de las excepciones que fueron opuestas por los demandados, {defendant.name}, solicitando que éstas sean rechazadas en todas sus partes,
        en atención a los argumentos de hecho y fundamentos de derecho que se exponen a continuación:
        """
        prompt = f"""
        Generate an opening for a text that responds to exceptions raise by the defendants in a legal case, to do so, fill the following template in {self.locale},
        adjust, add, or remove information where needed:
        <template>{template}</template>
        
		Consider the following information:
        <plaintiffs>{[x.name for x in self.input.plaintiffs or []]}</plaintiffs>
        <sponsoring-attorneys>{[x.name for x in self.input.sponsoring_attorneys or []]}</sponsoring-attorneys>
        <defendants>{[x.name for x in self.input.defendants or []]}</defendants>
        <case-title>{self.input.case_title}</case-title>
        <case-role>{self.input.case_role}</case-role>
        <current-date>{datetime.today().strftime('%Y-%m-%d')}</current-date>

        When answering:
        - Use an impersonal tone.
        - Do not use example or fake information.
        - Replace and adjust placeholder values and text around them to keep proper grammar and casing.
        - Remove placeholders that you lack information for, adjust text around them so it reads naturally.
        - Do not add text or indicators for what comes next, return only the opening.
        """
        response: Response = self.generator_llm.invoke(prompt)
        return response.text or "Abogado por el ejecutante, a US., con respeto digo"

    def _generate_exception_responses(self, exceptions: list[JudicialCollectionDemandExceptionRequest], demand_text: str) -> list[str] | None:

        def process_exception(nature: LegalException, context: str, index: int) -> tuple[int, str | None]:
            template = f"""
            Respecto de la excepcion de {nature.to_localized_string(self.locale)}: {{defendant_thesis + plaintiff_rebuttal}}.
            """
            prompt = f"""
            As an assistant to the plaintiffs of a legal case about judicial collection, your task is to generate an answer to a legal exception raised by
            the defendants in {self.locale}.

            In order to respond, consider the following template and adjust information where needed, you also have to generate the defendant_thesis and
            plaintiff_rebuttal sections:
            <template>{template}</template>

            Consider the nature and context of the exception:
            <exception-nature>{nature.value}</exception-nature>
            <exception-context>{context}</exception-context>

            Consider the contents of the original demand text redacted by the plaintiffs:
            <demand-text>{demand_text}</demand-text>

            Do also consider the following information:
            <exception-date>{self.input.request_date}</exception-date>
            <current-date>{datetime.today().strftime('%Y-%m-%d')}</current-date>

            To guide your output, consider the following example response to an 17a_debt_prescription exception:
            <example-response>
            Respecto de la excepción de prescripción: solo resta señalar que, conforme consta
            del título original que se encuentra en custodia del Tribunal, y de los hechos expuestos en el
            libelo de demanda, la fecha de vencimiento de la obligación corresponde al 03 de junio de
            2021, con lo cual, sólo había transcurrido poco más de un mes desde el vencimiento de la
            obligación cuando la demanda de liquidación fue presentada, y apenas cuatro meses, a la fecha
            en que la demanda fue notificada.
            En consecuencia, resulta manifiesto que no se configuran los presupuestos para alegar
            la prescripción de la acción ejecutiva, pues no alcanzó a transcurrir un año entre la fecha de
            vencimiento de la obligación, y la fecha en que fue notificada la demanda de liquidación.
            Por todo lo anterior, la presente excepción de prescripción debe ser rechazada en todas
            sus partes.
            </example-response>

            When answering:
            - Use an impersonal tone.
            - Do not use example or fake information.
            - Do not bold or italicize words, do not use markdown language.
            - Do not add section indicators for your thessis and rebuttal, just the content.
            - If an amount is not CLP, you must indicate the currency type after the amount, for example in the case of USD: $1.000.000.- USD"
            - Replace and adjust placeholder values and text around them to keep proper grammar and casing.
            - Remove placeholders that you lack information for, adjust text around them so it reads naturally.
            """
            if self.input.suggestion:
                prompt += f"""
                Consider that an assistant has come up with a strong suggestion for all exceptions, use it to guide your response only where relevant to the exception at hand:
                <suggestion>{self.input.suggestion}</suggestion>
                """
            response: Response = self.generator_llm.invoke(prompt)
            return index, response.text

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [
                executor.submit(process_exception, exception.nature, exception.context or "", idx)
                for idx, exception in enumerate(exceptions)
            ]
            results = []
            for future in as_completed(futures):
                index, result = future.result()
                if result:
                    results.append((index, result))
        
        results.sort(key=lambda x: x[0])
        exception_responses = [
            f"{i + 1}) {exception_response}"
            for i, exception_response in enumerate([result for _, result in results])
        ]
        return exception_responses

    def _generate_main_request(self) -> str:
        prompt = f"""
        Generate a formal legal statement in {self.locale} that conveys a request using an impersonal tone, formal legal vocabulary, and complex sentence structure.
        The language should reflect a high level of authority and precision, similar to how official legal documents are written.

        Consider the following template, localize it and modify it as you see fit:
        <template>
        POR TANTO,
        
        RUEGO A US. tener por evacuado el traslado conferido con fecha {{request_date (format_example: 12 de octubre de 2021)}} y, en su mérito, se rechace cada una de las excepciones hechas valer por el demandado, con expresa condena en costas.
        </template>"

        For context consider:
        <request-date>{self.input.request_date}</request-date>

        When answering:
        - If you lack context for a placeholder value, do not use fake or example information, write it out and adjust the text around it so it reads naturally.
        """
        main_request: Response = self.generator_llm.invoke(prompt)
        return main_request.text or "POR TANTO,\n\nRUEGO A US. Tener por evacuado el traslado conferido y, en su mérito, se rechace cada una de las excepciones hechas valer por el demandado, con expresa condena en costas."

    def _generate_additional_requests(self) -> str | None:
        segments: list[str] = []
        affix = "OTROSÍ"
        for secondary_request in self.input.secondary_requests or []:
            if secondary_request.nature:
                data = {}
                if secondary_request.nature == LegalExceptionRequest.INCLUDE_DOCUMENTS and self.input.suggestion:
                    data["suggestion"] = self.input.suggestion
                elif secondary_request.nature == LegalExceptionRequest.OTHER:
                    data = self.input.model_dump(exclude={"attorneys", "secondary_requests"})
                prompt = secondary_request.nature.get_prompt(secondary_request.context or "", data, self.locale)
                try:
                    request: Response = self.generator_llm.invoke(prompt)
                except Exception as e:
                    logging.warning(f"Could not generate additional request: {e}")
                    continue
                segments.append(request.text)
        if len(segments) == 0:
            return None
        numbered_segments = [f"{int_to_ordinal(i + 1, self.locale)} {affix}: {segment}" for i, segment in enumerate(segments)]
        return "\n\n".join(numbered_segments)

    def _self_generate_additional_requests(self, opening: str | None = None) -> None:
        requests_descriptions = "\n".join(
            f"- <request-type><value>{item.value}</value><description>{item.to_localized_string(Locale.EN_US)}</description></request-type>"
            for item in LegalExceptionRequest if item not in [LegalExceptionRequest.MEANS_OF_PROOF, LegalExceptionRequest.SPONSORSHIP_AND_POWER, LegalExceptionRequest.ACCREDIT_PERSONALITY]
        )
        prompt = f"""
        In the context of a legal case, consider the following list of request types that attorneys can include when answering to exceptions:
        {requests_descriptions}

        Given this suggestion:
        <suggestion>{self.input.suggestion}</suggestion>
        """
        if opening:
            prompt += f"""
            As well of the opening paragraph already redacted:
            <opening>{opening}</opening>
            """
        prompt += f"""
        Your job is to indicate the request or requests that could be included in the document, if any, by their value field, alongside relevant context for that exception.
        Do not indicate include_documents unless you can provide context that pinpoints specific documents brought up by the suggestion or opening.
        """
        response: AdditionalRequests = self.requests_llm.invoke(prompt)
        if response.requests:
            self.input.secondary_requests = response.requests
