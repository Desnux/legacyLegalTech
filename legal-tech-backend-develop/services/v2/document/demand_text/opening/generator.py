import time

from services.v2.document.base import BaseGenerator, Metrics, Response
from .models import DemandTextOpeningGeneratorInput, DemandTextOpeningGeneratorOutput, DemandTextOpeningStructure


class DemandTextOpeningGenerator(BaseGenerator):
    """Demand text opening generator."""

    def __init__(self, input: DemandTextOpeningGeneratorInput) -> None:
        super().__init__()
        self.input = input
        self.generator = self._create_structured_generator(Response)
        
    def generate(self) -> DemandTextOpeningGeneratorOutput:
        """Generate opening structure from input."""
        metrics = Metrics(label="DemandTextOpeningGenerator.generate")
        start_time = time.time()

        response: Response = self.generator.invoke(self._create_prompt())
        structure = DemandTextOpeningStructure(content=response.output)
        structure.normalize()
        metrics.llm_invocations += 1

        metrics.time = round(time.time() - start_time, 4)
        return DemandTextOpeningGeneratorOutput(metrics=metrics, structured_output=structure if structure is not None else None)
    
    def _create_content(self) -> str:
        lines: list[str] = []
        document_count = self.input.document_count or 0

        # Plaintiffs line
        current_line = ""
        if sponsoring_attorneys := self.input.sponsoring_attorneys:
            attorney_names = [attorney.name for attorney in sponsoring_attorneys if attorney.name]
            if len(attorney_names) == 1:
                current_line += f"{attorney_names[0]}, abogado, "
            elif len(attorney_names) == 2:
                current_line += f"{attorney_names[0]} y {attorney_names[1]}, abogados, "
            elif len(attorney_names) > 2:
                current_line += f"{', '.join(attorney_names[:-1])} y {attorney_names[-1]}, abogados, "
            else:
                current_line += ""
        lines.append(current_line)

        # Debtors line

        # Document line
        if document_count > 0:
            current_line = "Mi mandante, "
            if creditor := self.input.creditor:
                if name := creditor.name:
                    current_line += f"{name},"
            if document_count > 1:
                current_line += "es dueño y beneficiario de los siguientes documentos:"
            else:
                current_line += "es dueño y beneficiario del siguiente documento:"
            lines.append(current_line)
        return "\n\n".join(lines)

    def _create_prompt(self) -> str:
        information = {
            "creditor_sponsoring_attorneys": self.input.sponsoring_attorneys or [],
            "creditor": self.input.creditor,
            "creditor_legal_representatives": self.input.legal_representatives or [],
            "debtors": self.input.debtors or [],
            "co_debtors": self.input.co_debtors or [],
        }
        prompt = f"""
        Your task is to generate the opening of a demand about missing payments, before introducing more specific legal arguments.

        In order to do this, consider the following information:
        <information>{information}</information>

        Consider the following template, you are allowed to modify the template as you see fit:
        <template>{self._create_template()}</template>

        When answering:
        - Generate your response in es_ES.
        - Consider that the information may match template placeholders values regardless of differences in plurality.
        - Adjust the inserted information and/or the text around it to ensure the result reads naturally, for example when dealing with plural or singular entities.
        - Use titlecase when filling up names and addresses, but do not change the casing of abbreviations, for example, SpA, S.A, L.M. must remain as is.
        - Do not use fake or example data to replace placeholders, use only real data provided inside the information tags.
        - If you are missing information to replace a placeholder, or the replacement would be a null value, remove the placeholder from the filled template and adjust the text around it so it reads naturally, NEVER leave a placeholder in.
        - Add honorifics to names of people other than attorneys, such as don or doña, exclude them from names of groups, businesses or institutions.
        - For each pair of addresses (creditor section and debtor section) apply the rule independently:
          • If the two addresses are the same, replace the whole phrase with "ambos con domicilio en {{address}}".
          • If they are different, write "con domicilio en {{address1}} y {{address2}}, respectivamente".
        - IMPORTANT: creditor_legal_representatives belong ONLY to the creditor. Never use them as debtor representatives.
        - Debtor representatives must be taken ONLY from the corresponding debtor inside "debtors" (its legal_representatives). If none exist, do NOT mention a debtor representative.
        - IMPORTANT: "legal_representatives" at the root level belong ONLY to the PLAINTIFF (creditor).
        - NEVER use plaintiff legal representatives as debtor or co-debtor (aval).
        - The co-debtor (aval) NEVER has a legal representative unless explicitly stated inside its own object.
        - If a co-debtor (aval) has no legal_representatives in its data, do NOT mention any representative for the aval.
        """
        return prompt

    def _create_template(self) -> str:
        lines: list[str] = []
        document_count = self.input.document_count or 0
        lines.extend([
            (
                "{creditor_sponsoring_attorney.name}, abogado, domiciliado en "
                "{creditor_sponsoring_attorney.address}, mandatario judicial, en representación "
                "convencional, según se acreditará, de {creditor.name}, "
                "{creditor_economic_activity}, Rol Único Tributario N° {creditor.identifier}, "
                "representado legalmente por {creditor_legal_representative.name}, cédula de identidad N° "
                "{creditor_legal_representative.identifier}, {creditor_legal_representative.occupation}, "
                "ambos con domicilio en {creditor.address}, a US. "
                "respetuosamente digo:"
            ),
            (
                "Que en la representación que invisto, vengo en interponer la presente demanda "
                "ejecutiva en contra de {debtor.name}, {debtor_economic_activity}, Rol Único Tributario N° "
                "{debtor.identifier}, con domicilio para estos efectos en {debtor.address}, "
                "[SI Y SOLO SI el deudor es persona jurídica y en <information> existe(n) legal_representatives para este deudor: "
                "agregar a continuación ', representada legalmente por <NOMBRE(S) REPRESENTANTE(S)>', y aplicar la regla de domicilios "
                "si corresponde], en su calidad de deudor principal, "
                "y en contra de {co_debtor.name}, ya individualizado, en su calidad de aval, fiador y "
                "codeudor solidario, en base de las consideraciones que a continuación paso a exponer:"
            ),

        ])
        if document_count > 1:
            lines.append("Mi mandante, {creditor.name}, es dueño y beneficiario de los siguientes documentos:")
        elif document_count == 1:
            lines.append("Mi mandante, {creditor.name}, es dueño y beneficiario del siguiente documento:")
        return "\n\n".join(lines)
