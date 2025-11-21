import logging
from datetime import datetime

from pydantic import BaseModel, Field

from models.pydantic import (
    CorrectionSecondaryRequest,
    DemandTextCorrection,
    DemandTextCorrectionInput,
    DemandTextCorrectionSecondaryRequest,
    DispatchResolutionStructure,
    JudicialCollectionDemandTextStructure,
    Locale,
)
from util import int_to_ordinal
from .base_generator import BaseGenerator


class AdditionalRequests(BaseModel):
    requests: list[DemandTextCorrectionSecondaryRequest] | None = Field(None, description="Additional requests to include in the correction, if any")


class Response(BaseModel):
    text: str | None = Field(None, description="Generation output")


class DemandTextCorrectionGenerator(BaseGenerator):
    def __init__(self, input: DemandTextCorrectionInput, locale: Locale = Locale.ES_ES) -> None:
        self.input = input
        self.generator_llm = self.get_structured_generator(Response)
        self.requests_llm = self.get_structured_generator(AdditionalRequests)
        self.locale = locale
    
    def generate(self, dispatch_resolution: DispatchResolutionStructure, demand_text: JudicialCollectionDemandTextStructure) -> DemandTextCorrection:
        demand_text_content = demand_text.model_dump_json(include={"opening", "missing_payment_arguments", "main_request", "additional_requests"})
        court = self._generate_court()
        opening = self._generate_opening()
        corrections = self._generate_corrections(dispatch_resolution.to_raw_text(), demand_text_content)
        main_request = self._generate_main_request()

        if self.input.suggestion and self.input.secondary_requests is None:
            try:
                self._self_generate_additional_requests(corrections)
            except Exception as e:
                logging.warning(f"Could not self generate additional requests for demand text correction: {e}")

        summary = self._generate_summary()
        additional_requests = self._generate_additional_requests()

        return DemandTextCorrection(
            summary=summary,
            court=court,
            opening=opening,
            corrections=corrections,
            main_request=main_request,
            additional_requests=additional_requests,
        )
    
    def _generate_summary(self) -> str | None:
        segments: list[str] = []
        secondary_segments: list[str] = []
        affix = "OTROSÍ"
        segments.append("EN LO PRINCIPAL: RECTIFICA DEMANDA")

        for secondary_request in self.input.secondary_requests or []:
            if secondary_request.nature:
                if secondary_request.nature == CorrectionSecondaryRequest.OTHER and secondary_request.context:
                    prompt = f"Generate a brief and formal legal sentence in {self.locale} that summarizes a request or obligation using an impersonal tone in less than 8 words."
                    prompt += f"\nFor context of the request or obligation, consider: <context>{secondary_request.context}</context>"
                    try:
                        request: Response = self.generator_llm.invoke(prompt)
                    except Exception as e:
                        logging.warning(f"Could not generate additional request summary: {e}")
                        continue
                    if request and request.text:
                        secondary_segments.append(request.text.upper())
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
        {sponsoring_attorney.name}, abogado, por el ejecutante, {plaintiff.name}, en los autos caratulados “{case_title}”, ROL {case_role}, a US., con respeto digo:\n\n
        """
        prompt = f"""
        Generate an opening for a text of corrections in a legal case, to do so, fill the following template in {self.locale}, adjust, add, or remove information where needed:
        <template>{template}</template>
        
		Consider the following information:
        <sponsoring-attorneys>{[x.name for x in self.input.attorneys or []]}</sponsoring-attorneys>
        <case-title>{self.input.case_title}</case-title>
        <case-role>{self.input.case_role}</case-role>
        <current-date>{datetime.today().strftime('%Y-%m-%d')}</current-date>

        When answering:
        - Use an impersonal tone.
        - Do not use example or fake information.
        - Replace and adjust placeholder values and text around them to keep proper grammar and casing.
        - Remove placeholders that you lack information for, adjust text around them so it reads naturally.
        """
        response: Response = self.generator_llm.invoke(prompt)
        return response.text or "Abogado por el ejecutante, a US., con respeto digo"

    def _generate_corrections(self, dispatch_resolution: str, demand_text: str) -> str | None:
        template = """
        Vengo en rectificar la demanda, en el sentido de aclarar que {response_body}
        """
        prompt = f"""
        As an assistant to the plaintiffs of a legal case about judicial collection, your task is to generate corrections to the demand text in {self.locale},
        given what was raised by the court in the the following resolution:
        <resolution>{dispatch_resolution}</resolution>

        In order to respond, consider the following template and adjust information where needed, you also have to generate the response_body section:
        <template>{template}</template>

        Consider the contents of the original demand text redacted by the plaintiffs:
        <demand-text>{demand_text}</demand-text>

        Do also consider the following information:
        <current-date>{datetime.today().strftime('%Y-%m-%d')}</current-date>
        
        Consider this examples to understand what may change between an original demand text and its corrected segments:
        <example-original>
        3.- Parcela 182, ubicada en Peñablanca, sector C del plano archivado bajo el N°89 en el
		Registro de documentos del año 1956, a cargo del Conservador de Bienes Raíces de Limache.
		Propiedad inscrita en el Conservador de Bienes Raíces de Villa Alemana a Fojas 989 vta.,
		N°1545, del año 2017. el Conservador de Bienes Raíces de Villa Alemana, a Fojas 988 vta,
		N°1543 del año 2017. Cabe destacar que el inmueble cuenta con hipoteca a favor de Banco
		Consorcio, inscrita a Fojas 1267 N° 1375 del año 2017.
        </example-original>
        <example-correction>
        Vengo en rectificar la demanda, en el sentido de aclarar que el inmueble individualizado 
        en el Nº3) del tercer otrosí debe ser: Parcela 182, ubicada en Peñablanca, sector C del 
        plano archivado bajo el Nº89 en el Registro de documentos del año 1956, a cargo del
        Conservador de Bienes Raíces de Limache. Propiedad inscrita en el Conservador de Bienes
        Raíces de Villa Alemana a Fojas 989 vta., Nº1545, del año 2017.
        </example-correction>

        When answering:
        - Use an impersonal tone.
        - Do not use example or fake information.
        - If an amount is not CLP, you must indicate the currency type after the amount, for example in the case of USD: $1.000.000.- USD"
        - Replace and adjust placeholder values and text around them to keep proper grammar and casing.
        - Remove placeholders that you lack information for, adjust text around them so it reads naturally.
        """
        if self.input.suggestion:
            prompt += f"""
            Consider that an assistant has come up with a strong suggestion, use it to guide your corrections:
            <suggestion>{self.input.suggestion}</suggestion>
            """
        response: Response = self.generator_llm.invoke(prompt)
        return response.text

    def _generate_main_request(self) -> str:
        return "POR TANTO,\n\nRUEGO A US. Tenerlo rectificado en el sentido expuesto."

    def _generate_additional_requests(self) -> str | None:
        segments: list[str] = []
        affix = "OTROSÍ"
        for secondary_request in self.input.secondary_requests or []:
            if secondary_request.nature:
                data = {}
                if secondary_request.nature == CorrectionSecondaryRequest.INCLUDE_DOCUMENTS and self.input.suggestion:
                    data["suggestion"] = self.input.suggestion
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

    def _self_generate_additional_requests(self, corrections: str | None = None) -> None:
        requests_descriptions = "\n".join(
            f"- <request-type><value>{item.value}</value><description>{item.to_localized_string(Locale.EN_US)}</description></request-type>"
            for item in CorrectionSecondaryRequest
        )
        prompt = f"""
        In the context of a legal case, consider the following list of request types that attorneys can include when fixing their initial demand text:
        {requests_descriptions}

        Given this suggestion:
        <suggestion>{self.input.suggestion}</suggestion>
        """
        if corrections:
            prompt += f"""
            As well of the corrections already redacted:
            <corrections>{corrections}</corrections>
            """
        prompt += f"""
        Your job is to indicate the request or requests that could be included in the document, if any, by their value field, alongside relevant context.
        """
        response: AdditionalRequests = self.requests_llm.invoke(prompt)
        if response.requests:
            self.input.secondary_requests = response.requests
