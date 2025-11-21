from enum import Enum
from pydantic import Field

from models.pydantic import Attorney, Plaintiff, Defendant
from services.v2.document.base import InformationBaseModel, InputBaseModel, OutputBaseModel
from services.v2.document.demand_text import DemandTextStructure


class CompromiseRequest(str, Enum):
    AUTHORIZE_COPIES = "authorize_copies"
    CERTIFY_WHEN_APPROPRIATE = "certify_when_appropiate"

    def to_description_string(self, plural: bool) -> str:
        prefix = "ROGAMOS A US." if plural else "RUEGO A US."
        localized_strings = {
            CompromiseRequest.AUTHORIZE_COPIES: f"{prefix} decretar se otorgue copia autorizada de esta presentación, con los proveídos y notificación de las partes.",
            CompromiseRequest.CERTIFY_WHEN_APPROPRIATE: f"{prefix} ordenar a la Sra. Secretaria del tribunal certificar la ejecutoriedad de la resolución que apruebe el presente avenimiento en su oportunidad.",
        }
        return localized_strings.get(self, self.value)

    def to_localized_string(self) -> str:
        localized_strings = {
            CompromiseRequest.AUTHORIZE_COPIES: "COPIAS AUTORIZADAS",
            CompromiseRequest.CERTIFY_WHEN_APPROPRIATE: "SE CERTIFIQUE EN SU OPORTUNIDAD",
        }
        return localized_strings.get(self, self.value)


class CompromiseStructure(InformationBaseModel):
    """Compromise structure."""
    header: str | None = Field(None, description="Compromise header")
    summary: str | None = Field(None, description="Compromise summary")
    court: str | None = Field(None, description="Court the settlement is addressed to")
    opening: str | None = Field(None, description="Opening of the compromise")
    compromise_terms: str | None = Field(None, description="Terms of the compromise")
    main_request: str | None = Field(None, description="Compromise request to the court")
    additional_requests: str | None = Field(None, description="Additional requests of the compromise")


class CompromiseGeneratorInput(InputBaseModel):
    """Compromise generator input."""
    case_role: str | None = Field(None, description="Role of the legal case")
    case_title: str | None = Field(None, description="Legal case title")
    court_city: str | None = Field(None, description="City where the court is located, in titlecase")
    court_number: int | None = Field(None, description="Court number, if any, None otherwise")
    plaintiffs: list[Plaintiff] | None = Field(None, description="Plaintiffs in the legal case")
    sponsoring_attorneys: list[Attorney] | None = Field(None, description="Attorneys for the plaintiffs involved in the response")
    defendants: list[Defendant] | None = Field(None, description="Defendants in the legal case")
    defendant_attorneys: list[Attorney] | None = Field(None, description="Attorneys for the defendants involved in the response")
    secondary_requests: list[CompromiseRequest] | None = Field(None, description="Secondary requests to include in the compromise")
    demand_text: DemandTextStructure | None = Field(None, description="Demand text to consider")
    suggestion: str | None = Field(None, description="Suggestion to guide compromise terms and request generation")


class CompromiseGeneratorOutput(OutputBaseModel[CompromiseStructure]):
    """Compromise generator output."""
