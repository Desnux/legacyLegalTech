from enum import Enum

from pydantic import BaseModel, Field

from .attorney import Attorney
from .defendant import Defendant
from .locale import Locale
from .plaintiff import Plaintiff


class LegalCompromiseRequest(str, Enum):
    AUTHORIZE_COPIES = "authorize_copies"
    CERTIFY_WHEN_APPROPRIATE = "certify_when_appropiate"

    def to_description_string(self, locale: Locale, plural: bool) -> str:
        prefix = "ROGAMOS A US." if plural else "RUEGO A US."
        if locale == Locale.EN_US:
            prefix = "REQUEST TO US."
        localized_strings = {
            Locale.ES_ES: {
                LegalCompromiseRequest.AUTHORIZE_COPIES: f"{prefix} decretar se otorgue copia autorizada de esta presentación, con los proveídos y notificación de las partes.",
                LegalCompromiseRequest.CERTIFY_WHEN_APPROPRIATE: f"{prefix} ordenar a la Sra. Secretaria del tribunal certificar la ejecutoriedad de la resolución que apruebe el presente avenimiento en su oportunidad.",
            },
            Locale.EN_US: {
                LegalCompromiseRequest.AUTHORIZE_COPIES: f"{prefix} decree to be granted an authorized copy of this presentation, with the provisions and notification of the parties.",
                LegalCompromiseRequest.CERTIFY_WHEN_APPROPRIATE: f"{prefix} order the Secretary of the Court to certify the enforceability of the resolution approving this agreement in due course.",
            }
        }
        return localized_strings.get(locale, {}).get(self, self.value)

    def to_localized_string(self, locale: Locale) -> str:
        localized_strings = {
            Locale.ES_ES: {
                LegalCompromiseRequest.AUTHORIZE_COPIES: "COPIAS AUTORIZADAS",
                LegalCompromiseRequest.CERTIFY_WHEN_APPROPRIATE: "SE CERTIFIQUE EN SU OPORTUNIDAD",
            },
            Locale.EN_US: {
                LegalCompromiseRequest.AUTHORIZE_COPIES: "AUTHORIZE COPIES",
                LegalCompromiseRequest.CERTIFY_WHEN_APPROPRIATE: "CERTIFY WHEN APPROPIATE",
            }
        }
        return localized_strings.get(locale, {}).get(self, self.value)


class LegalCompromise(BaseModel):
    summary: str | None = Field(None, description="Summary of the requests")
    court: str | None = Field(None, description="Indicates the court to which the compromise is addressed")
    opening: str | None = Field(None, description="Opening of the compromise")
    compromise_terms: str | None = Field(None, description="Terms of the compromise")
    main_request: str | None = Field(None, description="Main request of the compromise")
    additional_requests: str | None = Field(None, description="Additional requests of the compromise")

    def to_raw_text(self) -> str | None:
        segments = filter(None, [
            self.summary,
            self.court,
            self.opening,
            self.compromise_terms,
            self.main_request,
            self.additional_requests,
        ])
        return "\n\n".join(segments) if segments else None


class LegalCompromiseInput(BaseModel):
    suggestion: str | None = Field(None, description="Compromise suggestion")
    case_title: str | None = Field(None, description="Legal case title")
    case_role: str | None = Field(None, description="Role of the legal case")
    court_city: str | None = Field(None, description="City where the court is located, in titlecase")
    court_number: int | None = Field(None, description="Court number, if any, None otherwise")
    plaintiffs: list[Plaintiff] | None = Field(None, description="Plaintiffs in the legal case")
    sponsoring_attorneys: list[Attorney] | None = Field(None, description="Attorneys for the plaintiffs involved in the response")
    defendants: list[Defendant] | None = Field(None, description="Defendants in the legal case")
    defendant_attorneys: list[Attorney] | None = Field(None, description="Attorneys for the defendants involved in the response")
    secondary_requests: list[LegalCompromiseRequest] | None = Field(None, description="Secondary requests that apply to the compromise")
