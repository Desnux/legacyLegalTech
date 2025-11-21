import random
from datetime import date, timedelta
from enum import Enum

from pydantic import BaseModel, Field

from .correction import CorrectionField, CorrectionFieldOption, CorrectionFieldType
from .creditor import Creditor
from .debtor import Debtor
from .enum import CurrencyType, Frequency
from .simulation import SimulationInput


class PromissoryNoteField(str, Enum):
    IDENTIFIER = "identifier"
    AMOUNT = "amount"
    AMOUNT_CURRENCY = "amount_currency"
    PAYMENT_INSTALLMENTS = "payment_installments"
    PAYMENT_FREQUENCY = "payment_frequency"
    AMOUNT_PER_INSTALLMENT = "amount_per_installment"
    AMOUNT_LAST_INSTALLMENT = "amount_last_installment"


class PromissoryNote(BaseModel):
    identifier: int | None = Field(None, description="Number that identifies the promissory note")
    amount: int | None = Field(None, description="Amount to pay")
    amount_currency: CurrencyType | None = Field(None, description="Currency of the amount")
    creation_date: date | None = Field(None, description="Creation date of the promissory note")
    payment_installments: int | None = Field(None, description="Number of installments with which to pay the amount")
    payment_frequency: Frequency | None = Field(None, description="Payment frequency, either 'monthly' or 'annually'")
    amount_per_installment: int | None = Field(None, description="Amount to pay for each or most installments")
    amount_last_installment: int | None = Field(None, description="Amount to pay for the last installment")
    due_payment_day: int | None = Field(None, description="Due day of the month for paying each or most installments")
    first_installment_date: date | None = Field(None, description="Due date for paying the first installment")
    last_installment_date: date | None = Field(None, description="Due date for paying the last installment")
    interest_rate: float | None = Field(None, description="Interest rate")
    interest_rate_frequency: Frequency | None = Field(None, description="Interest rate frequency, either 'monthly' or 'annually'")
    interest_rate_base_days: int | None = Field(None, description="Base used to calculate the interest rate frequency days")
    creditors: list[Creditor] | None = Field(None, description="Creditors or emitters of the promissory note")
    debtors: list[Debtor] | None = Field(None, description="Main debtors or suscribers of the promissory note")
    co_debtors: list[Debtor] | None = Field(None, description="Guaranteers or joint co-debtors of the promissory note")
    city: str | None = Field(None, description="City where the promissory note was made or signed")

    @classmethod
    def simulate(cls, input: SimulationInput, seed: int = 0) -> "PromissoryNote":
        local_random = random.Random(seed if seed != 0 else None)
        base_date = date.today()

        identifier = local_random.randint(1000000000, 9999999999)
        amount = local_random.randint(1000000, 9999999999)
        amount_currency = CurrencyType.CLP
        creation_date = base_date - timedelta(days=local_random.randint(0, 5 * 365))
        payment_installments = local_random.randint(1, 60)
        payment_frequency = local_random.choice([Frequency.MONTHLY, Frequency.ANNUALLY])

        if payment_installments > 1:
            amount_per_installment = amount // payment_installments
            amount_last_installment = amount - (amount_per_installment * (payment_installments - 1))
        else:
            amount_per_installment = amount
            amount_last_installment = amount

        due_payment_day = local_random.randint(1, 28)
        first_installment_date = creation_date + timedelta(days=local_random.randint(30, 180))
        if payment_frequency == Frequency.MONTHLY:
            last_installment_date = first_installment_date + timedelta(days=payment_installments * 30)
        else:
            last_installment_date = first_installment_date + timedelta(days=payment_installments * 365)
        
        interest_rate = round(local_random.uniform(0.01, 0.2), 4)
        interest_rate_frequency = local_random.choice([Frequency.MONTHLY, Frequency.ANNUALLY])
        interest_rate_base_days = local_random.choice([360, 365])

        return cls(
            identifier=identifier,
            amount=amount,
            amount_currency=amount_currency,
            creation_date=creation_date,
            payment_installments=payment_installments,
            payment_frequency=payment_frequency,
            amount_per_installment=amount_per_installment,
            amount_last_installment=amount_last_installment,
            due_payment_day=due_payment_day,
            first_installment_date=first_installment_date,
            last_installment_date=last_installment_date,
            interest_rate=interest_rate,
            interest_rate_frequency=interest_rate_frequency,
            interest_rate_base_days=interest_rate_base_days,
            creditors=input.creditors,
            debtors=input.debtors,
            co_debtors=input.co_debtors,
            city=input.court_city,
        )
    
    def get_prompt_reason(self) -> str:
        prompt = f"Consider the following promissory note attributes: <attributes>{self.model_dump()}</attributes>"
        prompt += f"\nGenerate a concise and realistic reason to raise the promissory note in a legal case about missing payments for simulation purposes, for example, missing installments from a certain date."
        return prompt
    
    def get_correction_fields(self) -> list[CorrectionField]:
        return [
            CorrectionField(
                label="Identificador",
                type=CorrectionFieldType.NUMBER,
                name=PromissoryNoteField.IDENTIFIER.value,
                initial_value=str(self.identifier) if self.identifier else None,
                options=None,
            ),
            CorrectionField(
                label="Monto del pagaré",
                type=CorrectionFieldType.NUMBER,
                name=PromissoryNoteField.AMOUNT.value,
                initial_value=str(self.amount) if self.amount else None,
                options=None,
            ),
            CorrectionField(
                label="Divisa del monto",
                type=CorrectionFieldType.SELECT,
                name=PromissoryNoteField.AMOUNT_CURRENCY.value,
                initial_value=self.amount_currency.value if self.amount_currency else None,
                options=[
                    CorrectionFieldOption(label=currency.name, value=currency.value)
                    for currency in CurrencyType
                ],
            ),
            CorrectionField(
                label="Cantidad de cuotas",
                type=CorrectionFieldType.NUMBER,
                name=PromissoryNoteField.PAYMENT_INSTALLMENTS.value,
                initial_value=str(self.payment_installments) if self.payment_installments else None,
                options=None,
            ),
            CorrectionField(
                label="Frecuencia de pago",
                type=CorrectionFieldType.SELECT,
                name=PromissoryNoteField.PAYMENT_FREQUENCY.value,
                initial_value=self.payment_frequency.value if self.payment_frequency else None,
                options=[
                    CorrectionFieldOption(label="Mensual", value=Frequency.MONTHLY.value),
                    CorrectionFieldOption(label="Anual", value=Frequency.ANNUALLY.value),
                ],
            ),
            CorrectionField(
                label="Monto por cuota",
                type=CorrectionFieldType.NUMBER,
                name=PromissoryNoteField.AMOUNT_PER_INSTALLMENT.value,
                initial_value=str(self.amount_per_installment) if self.amount_per_installment else None,
                options=None,
            ),
            CorrectionField(
                label="Monto última cuota",
                type=CorrectionFieldType.NUMBER,
                name=PromissoryNoteField.AMOUNT_LAST_INSTALLMENT.value,
                initial_value=str(self.amount_last_installment) if self.amount_last_installment else None,
                options=None,
            ),
        ]
    
    def normalize(self) -> None:
        if self.creditors:
            for creditor in self.creditors:
                creditor.normalize()
        if self.debtors:
            for debtor in self.debtors:
                debtor.normalize()
        if self.co_debtors:
            for co_debtor in self.co_debtors:
                co_debtor.normalize()
