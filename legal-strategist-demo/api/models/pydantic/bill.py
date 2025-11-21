import random
from datetime import date, timedelta
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from .correction import CorrectionField, CorrectionFieldOption, CorrectionFieldType
from .creditor import Creditor
from .debtor import Debtor
from .enum import CurrencyType
from .simulation import SimulationInput


class BillField(str, Enum):
    IDENTIFIER = "identifier"
    AMOUNT = "amount"
    AMOUNT_CURRENCY = "amount_currency"


class Bill(BaseModel):
    identifier: Optional[int] = Field(..., description="Number that identifies the bill")
    amount: Optional[int] = Field(..., description="Total amount to pay")
    amount_currency: Optional[CurrencyType] = Field(..., description="Currency of the amount, defaults to 'clp'")
    creation_date: Optional[date] = Field(..., description="Creation date of the bill")
    due_payment_date: Optional[date] = Field(..., description="Due date for paying the total amount")
    creditors: Optional[list[Creditor]] = Field(..., description="Creditors or emitters of the bill")
    debtors: Optional[list[Debtor]] = Field(..., description="Main debtors or suscribers of the bill")
    city: Optional[str] = Field(..., description="City where the bill was made or signed")

    @classmethod
    def simulate(cls, input: SimulationInput, seed: int = 0) -> "Bill":
        local_random = random.Random(seed if seed != 0 else None)
        base_date = date.today()

        identifier = local_random.randint(1000000000, 9999999999)
        amount = local_random.randint(1000000, 9999999999)
        amount_currency = CurrencyType.CLP
        creation_date = base_date - timedelta(days=local_random.randint(0, 5 * 365))
        due_payment_date = creation_date + timedelta(days=local_random.randint(30, 180))

        return cls(
            identifier=identifier,
            amount=amount,
            amount_currency=amount_currency,
            creation_date=creation_date,
            due_payment_date=due_payment_date,
            creditors=input.creditors,
            debtors=input.debtors,
            city=input.court_city,
        )
    
    def get_prompt_reason(self) -> str:
        prompt = f"Consider the following bill attributes: <attributes>{self.model_dump()}</attributes>"
        prompt += f"\nGenerate a concise and realistic reason to raise the bill in a legal case about missing payments for simulation purposes."
        return prompt
    
    def get_correction_fields(self) -> list[CorrectionField]:
        return [
            CorrectionField(
                label="Identificador",
                type=CorrectionFieldType.NUMBER,
                name=BillField.IDENTIFIER.value,
                initial_value=str(self.identifier) if self.identifier else None,
                options=None,
            ),
            CorrectionField(
                label="Monto de la factura",
                type=CorrectionFieldType.NUMBER,
                name=BillField.AMOUNT.value,
                initial_value=str(self.amount) if self.amount else None,
                options=None,
            ),
            CorrectionField(
                label="Divisa del monto",
                type=CorrectionFieldType.SELECT,
                name=BillField.AMOUNT_CURRENCY.value,
                initial_value=self.amount_currency.value if self.amount_currency else None,
                options=[
                    CorrectionFieldOption(label=currency.name, value=currency.value)
                    for currency in CurrencyType
                ],
            ),
        ]
    
    def normalize(self) -> None:
        if self.creditors:
            for creditor in self.creditors:
                creditor.normalize()
        if self.debtors:
            for debtor in self.debtors:
                debtor.normalize()
