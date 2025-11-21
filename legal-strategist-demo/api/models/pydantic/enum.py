from enum import Enum

from .locale import Locale


class ChatMessageSource(str, Enum):
    PLAINTIFFS = "plaintiffs"
    DEFENDANTS = "defendants"
    COURT = "court"


class CurrencyType(str, Enum):
    CLP = "clp"
    USD = "usd"


class DocumentType(str, Enum):
    DEMAND_TEXT = "demand_text"
    EXCEPTIONS = "exceptions"
    DISPATCH_RESOLUTION = "dispatch_resolution"
    RESOLUTION = "resolution"
    EXCEPTIONS_RESPONSE = "exceptions_response"
    DEMAND_TEXT_CORRECTION = "demand_text_correction"
    RESPONSE = "response"
    COMPROMISE = "compromise"
    REQUEST = "request"
    OTHER = "other"


class Frequency(str, Enum):
    MONTHLY = "monthly"
    ANNUALLY = "annually"


class LegalExceptionRequest(str, Enum):
    MEANS_OF_PROOF = "means_of_proof"
    INCLUDE_DOCUMENTS = "include_documents"
    INDICATE_EMAILS = "indicate_emails"
    ACCREDIT_PERSONALITY = "accredit_personality"
    SPONSORSHIP_AND_POWER = "sponsorship_and_power"
    SET_HEARING_DATE = "set_hearing_date"
    OTHER = "other"

    def get_prompt(self, context: str, data: dict, locale: Locale) -> str:
        prompt = f"Generate a formal legal statement in {locale} that conveys instructions or obligations using an impersonal tone, "
        prompt += f"formal legal vocabulary, and complex sentence structure. The language should reflect a high level of authority and precision, similar to how official legal documents are written."
        if self == LegalExceptionRequest.MEANS_OF_PROOF:
            prompt += f"\nConsider the following template, localize it and modify it as you see fit: <template>RUEGO A US. tener presente que mí parte se valdrá de los siguientes medios de prueba: instrumentos, testigos, confesión, inspección personal del Tribunal, peritos, y presunciones.</template>"
            prompt += f"\nConsider the following context for additional information to include, if any: <context>{context}</context>"
        elif self == LegalExceptionRequest.INCLUDE_DOCUMENTS:
            prompt += f"\nConsider the following template, localize it and modify it as you see fit: <template>RUEGO A US. tener por acompañados los documentos, con citación: ...</template>"
            prompt += f"\nConsider the following context and data to fill in the documents: <data>{data}</data> <context>{context}</context>"
        elif self == LegalExceptionRequest.INDICATE_EMAILS:
            prompt += f"\nConsider the following template, localize it and modify it as you see fit: <template>RUEGO A US. que en virtud del artículo 49 del Código de Procedimiento Civil, tener presente las casillas de correo electrónico que se indican a continuación, para efectos de notificación: ...</template>"
            prompt += f"\nConsider the following context to fill in the email addresses: <context>{context}</context>"
        elif self == LegalExceptionRequest.ACCREDIT_PERSONALITY:
            prompt += "\nConsider the following template, localize it and modify it as you see fit: <template>RUEGO A US. tener presente que mi personería para actuar en representación de {defendant.name}, consta de le escritura pública de mandato judicial, copia que vengo en acompañar en este acto, con citación.</template>"
            prompt += f"\nConsider the following context and data to fill in the defendants' names: <data>{data}</data> <context>{context}</context>"
        elif self == LegalExceptionRequest.SPONSORSHIP_AND_POWER:
            prompt += "\nConsider the following template, localize it and modify it as you see fit: <template>RUEGO A US. tener presente que, en mi calidad de abogado habilitado para el ejercicio de la profesión, y en virtud de las facultades que me fueron conferidas por medio de la personería acompañada en lo principal de esta presentación, actuaré personalmente en estos autos, asumiendo el patrocinio y poder en la presente causa, correspondiendo mi domicilio, para estos efectos, a aquél ubicado en {defendant_attorney.address}.</template>"
            prompt += "\nInclude the following template if there a delegations of power: <template-delegates>A su vez, RUEGO A US. tener presente que en este mismo acto, vengo en delegar poder, con las mismas facultades antes señaladas, en la abogada, {delegates_power_to.name}, cédula de identidad N° {delegates_power_to.identifier}, con domicilio en {delegates_power_to.address}.</template-delegates>"
            prompt += f"\nConsider the following context and data to fill in the sponsoring attorneys and delegates information, if any: <data>{data}</data> <context>{context}</context>"
        elif self == LegalExceptionRequest.SET_HEARING_DATE:
            prompt += "\nConsider the following template, localize it and modify it as you see fit: <template>RUEGO A US. se fije día y hora para celebrar audiencia en que se continúe la tramitación del juicio de oposición.</template>"
        else:
            prompt += f"\nIt should be legal request to a court inside a demand text about the following context: <context>{context}</context>"
            prompt += f"\nConsider the following template, localize it and modify it as you see fit: <template>RUEGO A US. tener presente ...</template>"
        return prompt

    def to_localized_string(self, locale: Locale) -> str:
        if locale == Locale.ES_ES:
            if self == LegalExceptionRequest.MEANS_OF_PROOF:
                return "MEDIOS DE PRUEBA"
            if self == LegalExceptionRequest.INCLUDE_DOCUMENTS:
                return "ACOMPAÑA DOCUMENTOS"
            if self == LegalExceptionRequest.INDICATE_EMAILS:
                return "SEÑALA CORREOS ELECTRÓNICOS"
            if self == LegalExceptionRequest.ACCREDIT_PERSONALITY:
                return "TENGA PRESENTE"
            if self == LegalExceptionRequest.SPONSORSHIP_AND_POWER:
                return "PATROCINIO Y PODER"
            if self == LegalExceptionRequest.SET_HEARING_DATE:
                return "SE FIJE DÍA Y HORA PARA AUDIENCIA"
        else:
            if self == LegalExceptionRequest.MEANS_OF_PROOF:
                return "MEANS OF PROOF"
            if self == LegalExceptionRequest.INCLUDE_DOCUMENTS:
                return "INCLUDE DOCUMENTS"
            if self == LegalExceptionRequest.INDICATE_EMAILS:
                return "INDICATE EMAILS"
            if self == LegalExceptionRequest.ACCREDIT_PERSONALITY:
                return "KEEP IN MIND"
            if self == LegalExceptionRequest.SPONSORSHIP_AND_POWER:
                return "SPONSORSHIP AND POWER"
            if self == LegalExceptionRequest.SET_HEARING_DATE:
                return "SET DAY AND TIME FOR HEARING"
        return self.value


class JudicialCollectionLegalRequirement(str, Enum):
    PHYSICAL_DOCUMENTS = "physical_documents"

    def get_prompt(self, context: str, data: dict, locale: Locale) -> str:
        prompt = f"Generate a formal legal request in {locale} that conveys instructions or obligations using an impersonal tone, "
        prompt += f"formal legal vocabulary, and complex sentence structure. The language should reflect a high level of authority and precision, similar to how official legal documents are written."
        if self == JudicialCollectionLegalRequirement.PHYSICAL_DOCUMENTS:
            prompt += f"\nConsider the following template, localize it and modify it as you see fit: <template>En cuanto a los documentos ofrecidos, deben ser acompañados físicamente en el tribunal ...</template>"
            prompt += f"\nConsider the following context for additional instructions to include, if any: <context>{context}</context>"
        else:
            prompt += f"\nIt should be legal request of a requirement from a court to a lawyer, about the following context: <context>{context}</context>"
        return prompt


class LegalSubject(str, Enum):
    BILL_COLLECTION = "bill_collection"
    PROMISSORY_NOTE_COLLECTION = "promisory_note_collection"
    GENERAL_COLLECTION = "general_collection"


class MissingPaymentDocumentType(str, Enum):
    BILL = "bill"
    BOND = "bond"
    PROMISSORY_NOTE = "promissory_note"


class StorageType(str, Enum):
    LOCAL = "local"
    S3 = "s3"
