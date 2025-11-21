from models.pydantic import MissingPaymentArgumentReason
from services.extractor.base_extractor import BaseExtractor


class MissingPaymentReasonExtractor(BaseExtractor):
    def __init__(self) -> None:
        self.extractor_llm = self.get_structured_extractor(MissingPaymentArgumentReason)

    def extract_from_text(self, text: str) -> MissingPaymentArgumentReason | None:
        reason: MissingPaymentArgumentReason = self.extractor_llm.invoke(self._get_prompt(text))
        if reason.reason is None:
            return None
        return reason

    def _get_prompt(self, source: str) -> str:
        prompt = f"Extract relevant missing payment attributes from this text: <text>{source}</text>"
        prompt += f"\nDO NOT create information from nothing, if an attribute is missing, you may use None or an equivalent value."
        return prompt