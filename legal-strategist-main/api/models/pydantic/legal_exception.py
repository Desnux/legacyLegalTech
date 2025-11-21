from enum import Enum

from .locale import Locale


class LegalException(str, Enum):
    COURT_INCOMPETENCE = "1a_court_incompetence"
    PLAINTIFF_INCOMPETENCE = "2a_plaintiff_incompetence"
    PENDING_LITIGATION = "3a_pending_litigation"
    CLAIM_LACKS_LEGAL_REQUIREMENTS = "4a_claim_lacks_legal_requirements"
    EXCUSSION_OR_BOND_EXPIRATION = "5a_excussion_or_bond_expiration"
    TITLE_FALSITY = "6a_title_falsity"
    TITLE_LACKS_REQUIREMENTS = "7a_title_lacks_requirements"
    EXCESS_OF_APPRAISAL = "8a_excess_of_appraisal"
    PAYMENT_OF_DEBT = "9a_payment_of_debt"
    REMISSION_OF_DEBT = "10a_remission_of_debt"
    GRANTING_OF_DELAYS = "11a_granting_of_delays"
    NOVATION = "12a_novation"
    COMPENSATION = "13a_compensation"
    NULLITY_OF_OBLIGATION = "14a_nullity_of_obligation"
    LOSS_OF_THING_OWNED = "15a_loss_of_thing_owned"
    TRANSACTION = "16a_transaction"
    DEBT_PRESCRIPTION = "17a_debt_prescription"
    RES_JUDICATA = "18a_res_judicata"

    def court_is_relevant(self) -> bool:
        if self == LegalException.COURT_INCOMPETENCE:
            return True
        if self == LegalException.TITLE_LACKS_REQUIREMENTS:
            return True
        if self == LegalException.GRANTING_OF_DELAYS:
            return True
        return False

    def demand_text_date_is_relevant(self) -> bool:
        if self == LegalException.COURT_INCOMPETENCE:
            return False
        if self == LegalException.EXCESS_OF_APPRAISAL:
            return False
        if self == LegalException.RES_JUDICATA:
            return False
        return True

    def plaintiffs_are_relevant(self) -> bool:
        if self == LegalException.COURT_INCOMPETENCE:
            return False
        if self == LegalException.GRANTING_OF_DELAYS:
            return False
        if self == LegalException.RES_JUDICATA:
            return False
        return True

    def plaintiff_attorneys_are_relevant(self) -> bool:
        if self == LegalException.PLAINTIFF_INCOMPETENCE:
            return True
        if self == LegalException.CLAIM_LACKS_LEGAL_REQUIREMENTS:
            return True
        if self == LegalException.TITLE_FALSITY:
            return True
        return False

    def get_prompt(self, context: str, data: dict, locale: Locale) -> str:
        prompt = f"Generate a formal legal statement in {locale} that conveys an exception or challenge using an assertive and plural tone, "
        prompt += f"formal legal vocabulary, and complex sentence structure. The language should reflect a high level of authority and precision, similar to how official legal documents are written."
        prompt += f"""
        \nConsider the following template, localize it and modify it as you see fit:
        <template>
        {self.to_localized_string(locale)}\n\nFundo la excepción en las siguientes consideraciones de hecho y de derecho que expongo: ...
        </template>
        """
        prompt += f"\nThe legal backbone behind the exception involves the article mentioned at the beginning of the template."
        prompt += f"\nConsider the following context and data for information to include, if any: <data>{data}</data> <context>{context}</context>"
        return prompt

    def to_localized_string(self, locale: Locale = Locale.EN_US) -> str:
        if locale == Locale.ES_ES:
            common = f"Nº {list(LegalException).index(self) + 1} del artículo 464 del Código de Procedimiento Civil, esto es,"
            if self == LegalException.COURT_INCOMPETENCE:
                return f"{common} la incompetencia del tribunal ante quien se haya presentado la demanda."
            if self == LegalException.PLAINTIFF_INCOMPETENCE:
                return f"{common} la falta de capacidad del demandante o de personería o representación legal del que comparezca en su nombre."
            if self == LegalException.PENDING_LITIGATION:
                return f"{common} la litis pendencia ante tribunal competente, siempre que el juicio que le da origen haya sido promovido por el acreedor, sea por vía de demanda o de reconvención."
            if self == LegalException.CLAIM_LACKS_LEGAL_REQUIREMENTS:
                return f"{common} la ineptitud de libelo por falta de algún requisito legal en el modo de formular la demanda, en conformidad a lo dispuesto en el artículo 254."
            if self == LegalException.EXCUSSION_OR_BOND_EXPIRATION:
                return f"{common} el beneficio de excusión o la caducidad de la fianza."
            if self == LegalException.TITLE_FALSITY:
                return f"{common} la falsedad del título."
            if self == LegalException.TITLE_LACKS_REQUIREMENTS:
                return f"{common} la falta de alguno de los requisitos o condiciones establecidos por las leyes para que dicho título tenga fuerza ejecutiva, sea absolutamente, sea con relación al demandado."
            if self == LegalException.EXCESS_OF_APPRAISAL:
                return f"{common} el exceso de avalúo en los casos de los incisos 2° y 3° del artículo 438."
            if self == LegalException.PAYMENT_OF_DEBT:
                return f"{common} el pago de la deuda."
            if self == LegalException.REMISSION_OF_DEBT:
                return f"{common} la remisión de la deuda."
            if self == LegalException.GRANTING_OF_DELAYS:
                return f"{common} la concesión de esperas o la prórroga del plazo."
            if self == LegalException.NOVATION:
                return f"{common} la novación."
            if self == LegalException.COMPENSATION:
                return f"{common} la compensación."
            if self == LegalException.NULLITY_OF_OBLIGATION:
                return f"{common} la nulidad de la obligación."
            if self == LegalException.LOSS_OF_THING_OWNED:
                return f"{common} la pérdida de la cosa debida, en conformidad a lo dispuesto en el Título XIX, Libro IV del Código Civil."
            if self == LegalException.TRANSACTION:
                return f"{common} la transacción."
            if self == LegalException.DEBT_PRESCRIPTION:
                return f"{common} la prescripción de la deuda o sólo de la acción ejecutiva."
            if self == LegalException.RES_JUDICATA:
                return f"{common} la cosa juzgada."
        else:
            common = f"Nº {list(LegalException).index(self) + 1} of article 464 of the Código de Procedimiento Civil, that is,"
            if self == LegalException.COURT_INCOMPETENCE:
                return f"{common} the incompetence of the court before which the claim has been filed."
            if self == LegalException.PLAINTIFF_INCOMPETENCE:
                return f"{common} the lack of capacity of the plaintiff or of legal representation or standing of the person appearing on his behalf."
            if self == LegalException.PENDING_LITIGATION:
                return f"{common} the pending litigation before a competent court, provided that the trial that gives rise to it has been initiated by the creditor, either by way of a claim or a counterclaim."
            if self == LegalException.CLAIM_LACKS_LEGAL_REQUIREMENTS:
                return f"{common} the ineptitude of the libel due to the lack of some legal requirement in the manner of formulating the claim, in accordance with the provisions of article 254."
            if self == LegalException.EXCUSSION_OR_BOND_EXPIRATION:
                return f"{common} the benefit of excussion or the expiration of the bond."
            if self == LegalException.TITLE_FALSITY:
                return f"{common} the falsity of the title."
            if self == LegalException.TITLE_LACKS_REQUIREMENTS:
                return f"{common} the lack of any of the requirements or conditions established by the laws for said title to have executive force, either absolutely or in relation to the defendant."
            if self == LegalException.EXCESS_OF_APPRAISAL:
                return f"{common} the excess of appraisal in the cases of paragraphs 2° and 3° of article 438."
            if self == LegalException.PAYMENT_OF_DEBT:
                return f"{common} the payment of the debt."
            if self == LegalException.REMISSION_OF_DEBT:
                return f"{common} the remission of the debt."
            if self == LegalException.GRANTING_OF_DELAYS:
                return f"{common} the granting of delays or extension of time."
            if self == LegalException.NOVATION:
                return f"{common} the novation."
            if self == LegalException.COMPENSATION:
                return f"{common} the compensation."
            if self == LegalException.NULLITY_OF_OBLIGATION:
                return f"{common} the nullity of the obligation."
            if self == LegalException.LOSS_OF_THING_OWNED:
                return f"{common} the loss of the thing owed, in accordance with the provisions of Title XIX, Book IV of the Código Civil."
            if self == LegalException.TRANSACTION:
                return f"{common} the transaction."
            if self == LegalException.DEBT_PRESCRIPTION:
                return f"{common} the prescription of the debt or only of the executive action."
            if self == LegalException.RES_JUDICATA:
                return f"{common} res judicata."
        return self.value