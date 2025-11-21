import time

from models.pydantic import JudicialCollectionLegalRequest, MissingPaymentDocumentType
from services.v2.document.base import BaseGenerator, Metrics, Response
from .models import (
    DemandTextAdditionalRequestGeneratorInput,
    DemandTextAdditionalRequestGeneratorOutput,
    DemandTextAdditionalRequestStructure,
)


class DemandTextAdditionalRequestGenerator(BaseGenerator):
    """Demant text additional request generator."""

    def __init__(self, input: DemandTextAdditionalRequestGeneratorInput) -> None:
        super().__init__()
        self.input = input
        self.generator = self._create_structured_generator(Response)
        self.plural = len(self.input.sponsoring_attorneys or []) > 1
    
    def generate(self) -> DemandTextAdditionalRequestGeneratorOutput:
        """Generate demand text additional request structure from input."""
        structure: DemandTextAdditionalRequestStructure | None = None
        metrics = Metrics(label="DemandTextAdditionalRequestGenerator.generate")
        start_time = time.time()

        if not self.input.nature:
            self.input.nature = JudicialCollectionLegalRequest.OTHER
        nature = self.input.nature
        if context := self.input.context:
            request: Response = self.generator.invoke(self._create_prompt(nature, context))
            metrics.llm_invocations += 1
            content = request.output.strip()
        else:
            content = self._create_content(nature)

        structure = DemandTextAdditionalRequestStructure(content=content)
        structure.normalize()

        metrics.time = round(time.time() - start_time, 4)
        return DemandTextAdditionalRequestGeneratorOutput(metrics=metrics, structured_output=structure if structure is not None else None)

    def _create_content(self, nature: JudicialCollectionLegalRequest) -> str | None:
        prefix = "ROGAMOS A US." if self.plural else "RUEGO A US."
        match nature:
            case JudicialCollectionLegalRequest.INDICATE_ASSETS_SEIZURE_GOODS_FOR_LOCKDOWN:
                if self.plural:
                    return "ROGAMOS A US. tener presente que señalamos para la traba del embargo todos los bienes del ejecutado que estime suficientes el Ministro de Fe encargado de la diligencia, pudiendo embargarlos a mera petición verbal del ejecutante."
                return "RUEGO A US. tener presente que señalo para la traba del embargo todos los bienes del ejecutado que estime suficientes el Ministro de Fe encargado de la diligencia, pudiendo embargarlos a mera petición verbal del ejecutante."
            case JudicialCollectionLegalRequest.APPOINT_PROVISIONAL_DEPOSITARY:
                if self.plural:
                    return "ROGAMOS A US. tener presente que designamos como depositario provisional de los bienes que se embarguen a los propios ejecutados, bajo su responsabilidad civil y criminal."
                return "RUEGO A US. tener presente que designo como depositario provisional de los bienes que se embarguen a los propios ejecutados, bajo su responsabilidad civil y criminal."
            case JudicialCollectionLegalRequest.INCLUDE_DOCUMENTS:
                description = ["documentos"]
                if document_types := self.input.document_types:
                    bill_count = sum(1 for document_type in document_types if document_type == MissingPaymentDocumentType.BILL)
                    promissory_note_count = sum(1 for document_type in document_types if document_type == MissingPaymentDocumentType.PROMISSORY_NOTE)
                    document_count = bill_count + promissory_note_count
                    if bill_count or promissory_note_count:
                        description = []
                    if bill_count == 1:
                        description.append("factura")
                    elif bill_count > 1:
                        description.append("facturas")
                    if promissory_note_count == 1:
                        description.append("pagaré")
                    elif promissory_note_count > 1:
                        description.append("pagarés")
                    if document_count == 1:
                        return f"{prefix} tener por acompañado, con citación, copia de {' y '.join(description)}, singularizado en lo principal de esta presentación, que corresponde al título fundante de esta ejecución."
                return f"{prefix} tener por acompañados, con citación, copia de {' y '.join(description)}, singularizados en lo principal de esta presentación, que corresponden a los títulos fundantes de esta ejecución."
            case JudicialCollectionLegalRequest.INDICATE_EMAILS:
                return f"{prefix} tener presente las casillas de correo electrónico existentes para efectos de notificación."
            case JudicialCollectionLegalRequest.ACCREDIT_PERSONALITY:
                if creditor := self.input.creditor:
                    if creditor.name:
                        if self.plural:
                            return f"ROGAMOS A US. tener presente que nuestra personería para actuar en representación de {creditor.name}, consta de le escritura pública de mandato judicial, copia que venimos en acompañar en este acto, con citación."
                        return f"RUEGO A US. tener presente que mi personería para actuar en representación de {creditor.name}, consta de le escritura pública de mandato judicial, copia que vengo en acompañar en este acto, con citación."
                if self.plural:
                    return f"ROGAMOS A US. tener presente que nuestra personería para actuar en representación del ejecutante, consta de le escritura pública de mandato judicial, copia que venimos en acompañar en este acto, con citación."
                return f"RUEGO A US. tener presente que mi personería para actuar en representación del ejecutante, consta de le escritura pública de mandato judicial, copia que vengo en acompañar en este acto, con citación."
            case JudicialCollectionLegalRequest.SPONSORSHIP_AND_POWER:
                if self.plural:
                    return "ROGAMOS A US. tener presente que, en nuestra calidad de abogados habilitados para el ejercicio de la profesión, y en virtud de las facultades que nos fueron conferidas por medio de la personería acompañada en lo principal de esta presentación, actuaremos personalmente en estos autos, asumiendo el patrocinio y poder en la presente causa, con las facultades de ambos incisos del Art. 7° del Código de Procedimiento Civil -que damos por expresamente reproducidas-."
                return "RUEGO A US. tener presente que, en mi calidad de abogado habilitado para el ejercicio de la profesión, y en virtud de las facultades que me fueron conferidas por medio de la personería acompañada en lo principal de esta presentación, actuaré personalmente en estos autos, asumiendo el patrocinio y poder en la presente causa, con las facultades de ambos incisos del Art. 7° del Código de Procedimiento Civil -que doy por expresamente reproducidas-."
            case JudicialCollectionLegalRequest.REQUEST_EXHORTATION:
                return f"{prefix} exhortar los presentes autos al juzgado competente. El exhorto deberá contener todos los antecedentes que resulten necesarios para su debida inteligencia."
            case JudicialCollectionLegalRequest.CPC_NOTIFICATION:
                return f"{prefix} se autorice desde ya al ministro de fe a practicar la notificación personal subsidiaria regulada en el artículo 44 del Código de Procedimiento Civil, tan pronto se certifiquen las búsquedas allí reguladas de conformidad con lo dispuesto en el artículo 69 inciso tercero del acta N° 71 del año 2016 de la Excelentísima Corte Suprema"
            case JudicialCollectionLegalRequest.OTHER:
                return None

    def _create_prompt(self, nature: JudicialCollectionLegalRequest, context: str) -> str:
        sub_prompt = ""
        match nature:
            case JudicialCollectionLegalRequest.INDICATE_ASSETS_SEIZURE_GOODS_FOR_LOCKDOWN:
                sub_prompt = f"""
                <specific-goods-example>
                - Camion marca Chevrolet modelo NQR 919, patente KRKG72, del año 2018 registrado a nombre de Via Uno Chile Spa.
                Además los siguientes bienes de propiedad del representante legal FELIPE FERNANDO PIZARRO CORRAL:
                - El inmueble inscrito a fojas 28278 Nº 37594 del Registro de Propiedad del Conservador de Bienes Raíces de Santiago del año 1981.
                - La participación accionaria o derechos en las siguientes sociedades: BERZINS Y PIZARRO LIMITADA, RUT Nº 77.437.070-6
                </specific-goods-example>
                <template>
                RUEGO A US. tener presente que señalo para la traba del embargo todos los bienes del ejecutado que estime suficientes el Ministro de Fe 
                encargado de la diligencia, pudiendo embargarlos a mera petición verbal del ejecutante. Particularmente, vengo en señalar los bienes que se
                indican a continuación:
                {{specific_goods}}"
                </template>
                """
            case JudicialCollectionLegalRequest.APPOINT_PROVISIONAL_DEPOSITARY:
                sub_prompt = f"""
                <specific-provisional-depository-example>
                don Felipe Fernando Pizarro Corral, don Juan Hidalgo López, y doña María Luis Joannes
                </specific-provisional-depository-example>
                <template>
                RUEGO A US. tener presente que designo como depositario provisional de los bienes que se embarguen a {{specific_provisional_depository}}, bajo su responsabilidad
                civil y criminal.
                </template>
                """
            case JudicialCollectionLegalRequest.INCLUDE_DOCUMENTS:
                sub_prompt = f"""
                <specific-documents-example>
                1. Pagaré singularizado en lo principal de esta presentación, que funda la presente ejecución, con sus respectivas hojas de prolongación.
                2. Certificados de dominio vigente e hipotecas y gravámenes, respecto de cada uno de los bienes inmuebles singularizados en el primer otrosí de esta presentación.
                3. Contratos de hipoteca Repertorios N° 12357-2021, 13883-2021 y 13882-2021, en los cuales consta la constitución de las garantías hipotecarias a favor de Banco Consorcio.
                </specific-documents-example>
                <template>
                RUEGO A US. tener por acompañados, con citación, copia de los siguientes documentos:
                {{specific_documents}}.
                </template>
                """
            case JudicialCollectionLegalRequest.INDICATE_EMAILS:
                sub_prompt = f"""
                <email-addresses-example>
                dbenavente@bypabogados.cl y jplana@bypabogados.cl.
                </email-addresses-example>
                <template>
                RUEGO A US. tener presente las casillas de correo electrónico que se indican a continuación, para efectos de notificación: {{email_addresses}}
                </template>
                """
            case JudicialCollectionLegalRequest.ACCREDIT_PERSONALITY:
                context = {"additional_context": context}
                if creditor := self.input.creditor:
                    if creditor.name:
                        context["plaintiff.name"] = creditor.name
                sub_prompt = f"""
                <template>
                RUEGO A US. tener presente que mi personería para actuar en representación de {{plaintiff.name}}, consta de le escritura pública de mandato
                judicial, copia que vengo en acompañar en este acto, con citación. {{additional_context}}
                </template>
                """
            case JudicialCollectionLegalRequest.SPONSORSHIP_AND_POWER:
                context = {"context": context}
                if sponsoring_attorneys := self.input.sponsoring_attorneys:
                    context["addresses"] = [attorney.address for attorney in sponsoring_attorneys if attorney.address]
                sub_prompt = f"""
                <template>
                RUEGO A US. tener presente que, en mi calidad de abogado habilitado para el ejercicio de la profesión, y en virtud de las facultades que me fueron conferidas por medio de la personería acompañada en lo principal de esta presentación, actuaré personalmente en estos autos, asumiendo el patrocinio y poder en la presente causa, con las facultades de ambos incisos del Art. 7° del Código de Procedimiento Civil -que doy por expresamente reproducidas-, correspondiendo mi domicilio, para estos efectos, a aquél ubicado en {{address}}.
                </template>

                Include the following template if there a delegations of power:
                <template-delegates>
                \n\n
                A su vez, RUEGO A US. tener presente que en este mismo acto, vengo en delegar poder, con las mismas facultades antes señaladas, en el abogado,
                {{delegates_power_to.name}}, cédula de identidad N° {{delegates_power_to.identifier}}, con domicilio en {{delegates_power_to.address}},
                quien podrá actuar en forma conjunta o separada con el suscrito -en forma indistinta-, y que firma en señal de aceptación.
                </template-delegates>
                """
            case JudicialCollectionLegalRequest.REQUEST_EXHORTATION:
                sub_prompt = f"""
                <filled-template-example>
                RUEGO A US. se exhorten los presentes autos al Juzgado Civil competente que corresponda de la ciudad de ANTOFAGASTA, a fin que éste, debidamente facultado, pueda decretar todas las diligencias que resulten necesarias, para notificar la demanda, requerir de pago y trabar embargo.
                El exhorto deberá contener todos los antecedentes que resulten necesarios para su debida inteligencia.
                </filled-template-example>
                <template>
                RUEGO A US. exhortar los presentes autos al Juzgado {{external_court_name_from_information}} ... {{reason_from_information}}. El exhorto deberá contener todos los antecedentes que resulten necesarios para su debida inteligencia.
                </template>
                """
            case JudicialCollectionLegalRequest.CPC_NOTIFICATION:
                context = {"additional_context": context}
                sub_prompt = f"""
                <template>
                RUEGO A US. se autorice desde ya al ministro de fe a practicar la notificación personal subsidiaria regulada en el artículo 44 del Código de Procedimiento Civil, tan pronto se certifiquen las búsquedas allí reguladas de conformidad con lo dispuesto en el artículo 69 inciso tercero del acta N° 71 del año 2016 de la Excelentísima Corte Suprema.
                {{additional_context}}
                </template>
                """
            case JudicialCollectionLegalRequest.OTHER:
                sub_prompt = f"""
                <template>
                RUEGO A US. {{request_from_information}}
                </template>
                """

        prompt = f"""
        Your task is to generate an additional request of a demand about missing payments.

        In order to do this, consider the following information:
        <information>{context}</information>
        
        Consider the following template and expected filled placeholder values format, you are allowed to modify the template as you see fit:
        {sub_prompt}

        When answering:
        - Generate your response in es_ES.
        {'- Use plural language, as if written by multiple sponsoring attorneys, for example, use ROGAMOS A US. instead of RUEGO A US.' if self.plural else ''}
        - Adjust the inserted information and/or the text around it to ensure the result reads naturally, for example when dealing with plural or singular entities.
        - Use titlecase when filling up names and addresses, but do not change the casing of abbreviations, for example, SpA, S.A, L.M. must remain as is.
        - Do not use fake or example data to replace placeholders, use only real data provided inside the information tags.
        - If you are missing information to replace a placeholder, remove the placeholder from the filled template and adjust the text around it so it reads naturally, NEVER leave a placeholder in.
        - If amount_currency is not CLP, you must indicate the currency type after amount or pending_amount, for example in the case of USD: $1.000.000.- USD
        - Add honorifics to names of people other than attorneys, such as don or doña, exclude them from names of groups, businesses or institutions.
        """
        return prompt
