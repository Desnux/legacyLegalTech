import logging
from datetime import date, datetime

from pydantic import BaseModel, Field

from models.pydantic import (
    DemandExceptionStructure,
    LegalResolution,
    LegalResolutionInput,
    Locale,
)
from .base_generator import BaseGenerator


class Response(BaseModel):
    text: str | None = Field(None, description="Generation output")


class LegalResolutionGenerator(BaseGenerator):
    def __init__(self, input: LegalResolutionInput, locale: Locale = Locale.ES_ES) -> None:
        self.input = input
        self.generator_llm = self.get_structured_generator(Response)
        self.locale = locale
    
    def generate_from_no_exceptions_request(self) -> LegalResolution:
        human_readable_issue_date = self._generate_human_readable_date(self.input.issue_date)
        header = self._generate_header("1. [120]Certifica que no se opuso excepciones")
        date_line = self._generate_date_line(human_readable_issue_date)
        resolution = self._generate_from_no_exceptions_request()
        return LegalResolution(
            header=header,
            date_line=date_line,
            resolution=resolution,
            city=self.input.court_city,
            readable_date=human_readable_issue_date,
        )
    
    def generate_from_demand_exception(self, demand_exception: DemandExceptionStructure) -> LegalResolution:
        human_readable_issue_date = self._generate_human_readable_date(self.input.issue_date)
        header = self._generate_header("1. [24]Recibe la causa a prueba")
        date_line = self._generate_date_line(human_readable_issue_date)
        footer = self._generate_footer(human_readable_issue_date)
        resolution = self._generate_resolution_from_demand_exception(demand_exception.to_raw_text())
        return LegalResolution(
            header=header,
            date_line=date_line,
            resolution=resolution,
            footer=footer,
            city=self.input.court_city,
            readable_date=human_readable_issue_date,
        )

    def _generate_date_line(self, readable_date: str | None) -> str | None:
        if readable_date and self.input.court_city:
            return f"{self.input.court_city.capitalize()}, {readable_date.lower()}."
        elif readable_date:
            return f"{readable_date.lower()}."
        elif self.input.court_city:
            return f"{self.input.court_city.capitalize()}."
        return None
    
    def _generate_header(self, nomenclature: str = "1. [67]Ordena despachar mandamiento") -> str | None:
        text = f"NOMENCLATURA : {nomenclature}"
        if self.input.court_number and self.input.court_city:
           text += f"\nJUZGADO : {self.input.court_number}º Juzgado Civil de {self.input.court_city}"
        elif self.input.court_city:
            text += f"\nJUZGADO : Juzgado Civil de {self.input.court_city}"
        if self.input.case_role:
            text += f"\nCAUSA ROL : {self.input.case_role}"
        if self.input.case_title:
            text += f"\nCARATULADO : {self.input.case_title}"
        return text
    
    def _generate_human_readable_date(self, query_date: date | None) -> str | None:
        if query_date is None:
            return None
        prompt = f"Given the following date: <date>{query_date}</date>"
        prompt += f"\nRewrite it with words in {self.locale} (format_example: dieciocho de febrero de dos mil veintiuno)"
        try:
            date_object: Response = self.generator_llm.invoke(prompt)
            return date_object.text or query_date.strftime('%Y-%m-%d')
        except Exception as e:
            logging.warning(f"Could not generate human readable date: {e}")
            return query_date.strftime('%Y-%m-%d')

    def _generate_from_no_exceptions_request(self) -> str | None:
        return "CERTIFICO: Que no hay constancia en autos que la parte demandada haya opuesto excepciones a la ejecución, dentro del plazo legal establecido para ello, el cual se encuentra vencido."

    def _generate_footer(self, readable_date: str | None) -> str | None:
        footer = ""
        if readable_date and self.input.court_city:
            footer = f"{self.input.court_city.capitalize()}, {readable_date.lower()}, "
        elif readable_date:
            footer = f"{readable_date.lower()}, "
        elif self.input.court_city:
            footer =  f"{self.input.court_city.capitalize()}, "
        if len(footer) > 0:
            footer += "se notificó por el estado diario, la resolución precedente."
        else:
            footer = "Se notificó por el estado diario, la resolución precedente."
        return footer if len(footer) > 0 else None

    def _generate_resolution_from_demand_exception(self, demand_exception: str) -> str:
        template = """
        A la presentación de fecha {request_date (format_example: 10 de febrero de 2021)}:
        
        A lo principal: Téngase por evacuado el traslado. {additional_request_responses (format_example: Al primer otrosí: Por acompañados, con citación. Al segundo otrosí: Estése a lo que se resolverá.)}

        Vistos:
        Se declaran admisibles las excepciones opuestas y se las recibe a prueba por el término legal, fijándose al efecto como hechos sustanciales,
        pertinentes y controvertidos los siguientes:
        {relevant_facts (format_example: 1.- Efectividad de tener, quien comparece a nombre de la demandante, personería o representación legal para comparecer a su nombre.\\n\\n2.- Existencia de un juicio iniciado entre las mismas partes, con el mismo objeto y causa de pedir. En la afirmativa, estado actual del proceso.)}
        """
        if self.input.hearing_hour and self.input.hearing_days:
            template += """

            Para la testimonial que deseen rendir las partes, se fijan las audiencias de los {hearing_days (format_example: [-2, 1] -> dos últimos días; [8, 9] -> días octavo y noveno)} del probatorio
            a las {hearing_hours (format_example: 10:00)} horas, y si el último día recayere en sábado se reemplazará por el día siguiente hábil a la misma hora.
            """
        prompt = f"""
        In the role of the court, generate a legal resolution in {self.locale} to the following exceptions raised by the defendants in a legal case related to missing payments:
        <exceptions>{demand_exception}</exceptions>

        In order to respond, consider the following template and adjust information where needed, you also have to generate the additional_request_responses and relevant_facts sections:
        <template>{template}</template>

        Consider the following information:
        <request-date>{self.input.request_date}</request-date>
        <current-data>{self.input.issue_date}</current-data>
        """
        if self.input.hearing_hour and self.input.hearing_days:
            prompt += f"""
            <hearing-hour>{self.input.hearing_hour}</hearing-hour>
            <hearing-days>{self.input.hearing_days}</hearing-days>
            """
        prompt += """
        When answering:
        - Use an impersonal tone.
        - Do not use example or fake information.
        - Do not bold or italicize words.
        - Replace and adjust placeholder values and text around them to keep proper grammar and casing.
        - Handle each additional request response in less than 16 words, in order to do this, acknowledge indications and designations (with a brief mention of what was indicated or designated) and give for accompanied any document or email from a request related to giving or sharing elements with the court.
        """
        response: Response = self.generator_llm.invoke(prompt)
        result = response.text or "Se declaran admisibles las excepciones opuestas y se las recibe a prueba por el término legal."
        return f"{result}\n\nNotifíquese por cédula."
