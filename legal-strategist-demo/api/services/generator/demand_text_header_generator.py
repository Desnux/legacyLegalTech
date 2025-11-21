from models.pydantic import LegalSubject, Litigant
from util import int_to_roman


class DemandTextHeaderGenerator:
    def __init__(self, legal_subject: LegalSubject) -> None:
        self.legal_subject = legal_subject

    def generate_from_litigants(self, plaintiffs: list[Litigant], sponsoring_attorneys: list[Litigant], defendants: list[Litigant]) -> str:
        text = "PROCEDIMIENTO : EJECUTIVO"
        if self.legal_subject == LegalSubject.PROMISSORY_NOTE_COLLECTION:
            text += "\nMATERIA : COBRO DE PAGARÉ"
        elif self.legal_subject == LegalSubject.BILL_COLLECTION:
            text += "\nMATERIA : COBRO DE FACTURA"
        else:
            text += "\nMATERIA : CUMPLIMIENTO OBLIGACIÓN DE DAR"

        for idx, plaintiff in enumerate(plaintiffs):
            if plaintiff.name:
                if len(plaintiffs) > 1:
                    text += f"\nDEMANDANTE {int_to_roman(idx + 1)} : {plaintiff.name.upper()}"
                else:
                    text += f"\nDEMANDANTE : {plaintiff.name.upper()}"
                if plaintiff.identifier:
                    text += f"\nRUT : {plaintiff.identifier.upper()}"

        for sponsoring_attorney in sponsoring_attorneys or []:
            if sponsoring_attorney.name:
                text += f"\nABOGADO PATROCINANTE : {sponsoring_attorney.name.upper()}"
                if sponsoring_attorney.identifier:
                    text += f"\nRUT : {sponsoring_attorney.identifier.upper()}"

        for idx, defendant in enumerate(defendants):
            if defendant.name:
                if len(defendants) > 1:
                    text += f"\nEJECUTADO {int_to_roman(idx + 1)} : {defendant.name.upper()}"
                else:
                    text += f"\nEJECUTADO : {defendant.name.upper()}"
                if defendant.identifier:
                    text += f"\nRUT : {defendant.identifier.upper()}"
                legal_representatives = defendant.legal_representatives or []
                for sub_idx, legal_representative in enumerate(legal_representatives):
                    if legal_representative.name and len(legal_representative.name) > 6:
                        if len(legal_representatives) > 1:
                            text += f"\nREPRESENTANTE {int_to_roman(sub_idx + 1)} : {legal_representative.name.upper()}"
                        else:
                            text += f"\nREPRESENTANTE : {legal_representative.name.upper()}"
                        if legal_representative.identifier:
                            text += f"\nRUT : {legal_representative.identifier.upper()}"
        return text
