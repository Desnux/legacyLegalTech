from enum import Enum

from .locale import Locale


DELEGATE_TEMPLATE = """
\n\n
A su vez, RUEGO A US. tener presente que en este mismo acto, vengo en delegar poder, con las mismas facultades antes señaladas, en la abogada,
{delegates_power_to.name}, cédula de identidad N° {delegates_power_to.identifier}, con domicilio en {delegates_power_to.address},
quien podrá actuar en forma conjunta o separada con el suscrito -en forma indistinta-, y que firma en señal de aceptación.
"""

SPECIFIC_GOODS_TEMPLATE = """
RUEGO A US. tener presente que señalo para la traba del embargo todos los bienes del ejecutado que estime suficientes el Ministro de Fe 
encargado de la diligencia, pudiendo embargarlos a mera petición verbal del ejecutante. Particularmente, vengo en señalar los bienes que se
indican a continuación:
{specific_goods}
"""

SPECIFIC_PROVISIONAL_DEPOSITARY = """
RUEGO A US. tener presente que designo como depositario provisional de los bienes que se embarguen a {context}, bajo su responsabilidad
civil y criminal.
"""

SPECIFIC_DOCUMENTS_TO_INCLUDE = """
RUEGO A US. tener por acompañados, con citación, copia de los siguientes documentos:
{context (format_hint: enumerate each valid item on a new line, ensuring clear separation between items)}.
"""

NO_EMAILS_TO_INDICATE = """
RUEGO A US. tener presente las casillas de correo electrónico para efectos de notificación.
"""

ACCREDIT_PERSONALITY_WITH_CONTEXT = """
RUEGO A US. tener presente que mi personería para actuar en representación de {plaintiff.name}, consta de le escritura pública de mandato
judicial, copia que vengo en acompañar en este acto, con citación. {context}
"""

REQUEST_EXHORTATION_WITHOUT_CONTEXT = """
RUEGO A US. exhortar los presentes autos al juzgado competente. El exhorto deberá contener todos los antecedentes que resulten necesarios para su debida inteligencia.
"""

class JudicialCollectionLegalRequest(str, Enum):
    INDICATE_ASSETS_SEIZURE_GOODS_FOR_LOCKDOWN = "indicate_asset_seizure_goods_for_lockdown"
    APPOINT_PROVISIONAL_DEPOSITARY = "appoint_provisional_depositary"
    INCLUDE_DOCUMENTS = "include_documents"
    INDICATE_EMAILS = "indicate_emails"
    ACCREDIT_PERSONALITY = "accredit_personality"
    SPONSORSHIP_AND_POWER = "sponsorship_and_power"
    REQUEST_EXHORTATION = "request_exhortation"
    CPC_NOTIFICATION = "cpc_notification"
    OTHER = "other"

    def get_prompt(self, context: str, data: dict, locale: Locale) -> str:
        template = self.get_template()
        prompt = f"""
        Your task is to generate a concise legal request in {locale} that conveys instructions or obligations using an impersonal tone, formal legal vocabulary,
        and complex sentence structure. The language should reflect a high level of authority and precision, similar to how official legal documents are written.
        """
        if self == JudicialCollectionLegalRequest.INDICATE_ASSETS_SEIZURE_GOODS_FOR_LOCKDOWN:
            prompt += f"""
            In this case, to indicate assets for a potential seizure of goods.
            Consider the following template: <template>{SPECIFIC_GOODS_TEMPLATE if len(context) > 0 else template}</template>",
            """
            if len(context) > 0:
                prompt += f"""
                Consider this context in order to produce the specific goods section: <context>{context}</context>
                Consider this example of specific goods output:
                <specific-goods-example>
                - Camion marca Chevrolet modelo NQR 919, patente KRKG72, del año 2018 registrado a nombre de Via Uno Chile Spa.
                Además los siguientes bienes de propiedad del representante legal FELIPE FERNANDO PIZARRO CORRAL:
                - El inmueble inscrito a fojas 28278 Nº 37594 del Registro de Propiedad del Conservador de Bienes Raíces de Santiago del año 1981.
                - La participación accionaria o derechos en las siguientes sociedades: BERZINS Y PIZARRO LIMITADA, RUT Nº 77.437.070-6
                </specific-goods-example>
                """
        elif self == JudicialCollectionLegalRequest.APPOINT_PROVISIONAL_DEPOSITARY:
            prompt += f"""
            In this case, to appoint a provisional depositary.
            Consider the following template: <template>{SPECIFIC_PROVISIONAL_DEPOSITARY if len(context) > 0 else template}</template>",
            """
            if len(context) > 0:
                prompt += f"\nConsider this context: <context>{context}</context>"
        elif self == JudicialCollectionLegalRequest.INCLUDE_DOCUMENTS:
            prompt += f"""
            In this case, to give for included the relevant documents.
            Consider the following template: <template>{SPECIFIC_DOCUMENTS_TO_INCLUDE if len(context) > 0 else template}</template>",
            """
            if len(context) > 0:
                prompt += f"\nConsider this context: <context>{context}</context>"
            if len(data) > 0:
                prompt += f"\nConsider this data: <data>{data}</data>"
        elif self == JudicialCollectionLegalRequest.INDICATE_EMAILS:
            prompt += f"""
            In this case, to indicate email addresses that the court use to notify the attorneys.
            Consider the following template: <template>{template if len(context) > 0 else NO_EMAILS_TO_INDICATE}</template>",
            """
            if len(context) > 0:
                prompt += f"\nConsider this context: <context>{context}</context>"
        elif self == JudicialCollectionLegalRequest.ACCREDIT_PERSONALITY:
            prompt += f"""
            In this case, to accredit that the sponsoring attorney or attorneys can act in behalf of the plaintiffs.
            Consider the following template: <template>{ACCREDIT_PERSONALITY_WITH_CONTEXT if len(context) > 0 else template}</template>",
            """
            if len(data) > 0:
                prompt += f"\nConsider this data: <data>{data}</data>"
            if len(context) > 0:
                prompt += f"\nConsider this context: <context>{context}</context>"
        elif self == JudicialCollectionLegalRequest.SPONSORSHIP_AND_POWER:
            prompt += f"""
            In this case, to assume sponsorship and power on behalf of the plaintiffs.
            Consider the following template: <template>{template}</template>",
            """
            if len(context) > 0:
                prompt += f"\nInclude the following template if there a delegations of power: <template-delegates>{DELEGATE_TEMPLATE}</template-delegates>"
            if len(data) > 0:
                prompt += f"\nConsider this data: <data>{data}</data>"
            if len(context) > 0:
                prompt += f"\nConsider this context: <context>{context}</context>"
        elif self == JudicialCollectionLegalRequest.REQUEST_EXHORTATION:
            prompt += f"""
            In this case, to request for an external court to get involved in the procedure.
            Consider the following template: <template>{template if len(context) > 0 else REQUEST_EXHORTATION_WITHOUT_CONTEXT}</template>",
            """
            if len(context) > 0:
                prompt += f"\nConsider this context: <context>{context}</context>"
        elif self == JudicialCollectionLegalRequest.CPC_NOTIFICATION:
            prompt += f"""
            In this case, to request that the defendants be notified about the procedure.
            Consider the following template: <template>{template}</template>",
            """
            if len(context) > 0:
                prompt += f"\nConsider this context: <context>{context}</context>"
        elif self == JudicialCollectionLegalRequest.OTHER:
            prompt += f"\nIt should be about the following context: <context>{context}</context>"
            prompt += "\nConsider the following template, localize it and modify it as you see fit: <template>RUEGO A US. tener presente {context}</template>"
        prompt += f"""
            When answering:
            - Generate your response in {locale}.
            - If there are no placeholder values to replace, stick close to the template, do not expand it even if you find it short, your objective is to be concise.
            """
        if len(data) > 0 or len(context) > 0:
            prompt += f"""
            - Context and data match placeholders regardless of differences in plurality.
            - You must adjust either the inserted data, context, and/or the text around them to ensure the result reads naturally, for example when dealing with plural or singular entities, or free form text attributes.
            - Do not use fake or example information, use only real information provided by the context or data.
            - If you are missing data or context for a placeholder, remove the placeholder from the filled template and adjust the text around it so it reads naturally, NEVER leave a placeholder in.
            """
        else:
            prompt += f"\n- Do not use fake or example information, you are allowed to remove sections of the template that would not make sense without more real context."
        return prompt
    
    def get_template(self) -> str:
        templates = {
            JudicialCollectionLegalRequest.INDICATE_ASSETS_SEIZURE_GOODS_FOR_LOCKDOWN:
                "RUEGO A US. tener presente que señalo para la traba del embargo todos los bienes del ejecutado que estime suficientes el Ministro de Fe encargado de la diligencia, pudiendo embargarlos a mera petición verbal del ejecutante.",
            JudicialCollectionLegalRequest.APPOINT_PROVISIONAL_DEPOSITARY:
                "RUEGO A US. tener presente que designo como depositario provisional de los bienes que se embarguen a los propios ejecutados, bajo su responsabilidad civil y criminal.",
            JudicialCollectionLegalRequest.INCLUDE_DOCUMENTS: 
                "RUEGO A US. tener por acompañados, con citación, copia de {documents.document_types}, singularizados en lo principal de esta presentación, que corresponden a los títulos fundantes de esta ejecución.",
            JudicialCollectionLegalRequest.INDICATE_EMAILS: 
                "RUEGO A US. tener presente las casillas de correo electrónico que se indican a continuación, para efectos de notificación: {context}",
            JudicialCollectionLegalRequest.ACCREDIT_PERSONALITY:
                "RUEGO A US. tener presente que mi personería para actuar en representación de {plaintiff.name}, consta de le escritura pública de mandato judicial, copia que vengo en acompañar en este acto, con citación.",
            JudicialCollectionLegalRequest.SPONSORSHIP_AND_POWER:
                "RUEGO A US. tener presente que, en mi calidad de abogado habilitado para el ejercicio de la profesión, y en virtud de las facultades que me fueron conferidas por medio de la personería acompañada en lo principal de esta presentación, actuaré personalmente en estos autos, asumiendo el patrocinio y poder en la presente causa, con las facultades de ambos incisos del Art. 7° del Código de Procedimiento Civil -que doy por expresamente reproducidas-, correspondiendo mi domicilio, para estos efectos, a aquél ubicado en {sponsoring_attorney.address}.",
            JudicialCollectionLegalRequest.REQUEST_EXHORTATION:
                "RUEGO A US. exhortar los presentes autos al Juzgado {external_court.name} ... {reason}. El exhorto deberá contener todos los antecedentes que resulten necesarios para su debida inteligencia.",
            JudicialCollectionLegalRequest.CPC_NOTIFICATION:
                "RUEGO A US. se autorice desde ya al ministro de fe a practicar la notificación personal subsidiaria regulada en el artículo 44 del Código de Procedimiento Civil, tan pronto se certifiquen las búsquedas allí reguladas de conformidad con lo dispuesto en el artículo 69 inciso tercero del acta N° 71 del año 2016 de la Excelentísima Corte Suprema",
        }
        return templates.get(self, self.value)

    def to_localized_string(self, locale: Locale) -> str:
        localized_strings = {
            Locale.ES_ES: {
                JudicialCollectionLegalRequest.INDICATE_ASSETS_SEIZURE_GOODS_FOR_LOCKDOWN: "SEÑALA BIENES PARA LA TRABA DEL EMBARGO",
                JudicialCollectionLegalRequest.APPOINT_PROVISIONAL_DEPOSITARY: "DESIGNA DEPOSITARIO PROVISIONAL",
                JudicialCollectionLegalRequest.INCLUDE_DOCUMENTS: "ACOMPAÑA DOCUMENTOS",
                JudicialCollectionLegalRequest.INDICATE_EMAILS: "SEÑALA CORREOS ELECTRÓNICOS",
                JudicialCollectionLegalRequest.ACCREDIT_PERSONALITY: "ACREDITA PERSONERÍA",
                JudicialCollectionLegalRequest.SPONSORSHIP_AND_POWER: "PATROCINIO Y PODER",
                JudicialCollectionLegalRequest.REQUEST_EXHORTATION: "SOLICITA EXHORTO",
                JudicialCollectionLegalRequest.CPC_NOTIFICATION: "NOTIFICACIÓN ART. 44 CPC.",
            },
            Locale.EN_US: {
                JudicialCollectionLegalRequest.INDICATE_ASSETS_SEIZURE_GOODS_FOR_LOCKDOWN: "INDICATE ASSETS SEIZURE GOODS FOR LOCKDOWN",
                JudicialCollectionLegalRequest.APPOINT_PROVISIONAL_DEPOSITARY: "APPOINT PROVISIONAL DEPOSITARY",
                JudicialCollectionLegalRequest.INCLUDE_DOCUMENTS: "INCLUDE DOCUMENTS",
                JudicialCollectionLegalRequest.INDICATE_EMAILS: "INDICATE EMAILS",
                JudicialCollectionLegalRequest.ACCREDIT_PERSONALITY: "ACCREDIT PERSONALITY",
                JudicialCollectionLegalRequest.SPONSORSHIP_AND_POWER: "SPONSORSHIP AND POWER",
                JudicialCollectionLegalRequest.REQUEST_EXHORTATION: "REQUEST EXHORTATION",
                JudicialCollectionLegalRequest.CPC_NOTIFICATION: "ART. 44 CPC. NOTIFICATION",
            }
        }
        return localized_strings.get(locale, {}).get(self, self.value)
