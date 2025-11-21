from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class CorrectionFieldType(str, Enum):
    STRING = "string"
    NUMBER = "number"
    SELECT = "select"
    LIST = "list"


class CorrectionFieldOption(BaseModel):
    label: str = Field(..., description="Human friendly label for the option")
    value: str = Field(..., description="Value associated to the option")


class CorrectionField(BaseModel):
    label: str = Field(..., description="Human friendly label for the field")
    type: CorrectionFieldType = Field(CorrectionFieldType.STRING, description="Field input type, either 'string', 'number', or 'select'")
    name: str = Field(..., description="Field unique identifier")
    initial_value: str | None = Field(None, description="Initial value of the field as a string, if any")
    options: list[CorrectionFieldOption] | None = Field(None, description="Options to choose from, only if input type is 'select'")
    corrected_value: str | None = Field(None, description="Corrected value of the field as a string, if any")

    def get_change(self) -> dict:
        return {"field_id": self.name, "previous_value": self.initial_value, "new_value": self.corrected_value}

    def has_changed(self) -> bool:
        return self.initial_value != self.corrected_value
    
    def update(self) -> None:
        self.initial_value = self.corrected_value
        self.corrected_value = None

class CorrectionFieldList(BaseModel):
    label: str = Field(..., description="Human friendly label for the field")
    type: Literal[CorrectionFieldType.LIST] = CorrectionFieldType.LIST
    name: str = Field(..., description="Field list unique identifier")
    initial_value: list[CorrectionField] = Field(default_factory=list, description="List of initial values")
    corrected_value: list[CorrectionField] = Field(default_factory=list, description="List of corrected values")

    def get_change(self) -> dict:
        return {
            "field_id": self.name,
            "sub_fields": [field.get_change() for field in self.corrected_value if field.has_changed()],
        }

    def has_changed(self) -> bool:
        if len(self.initial_value) != len(self.corrected_value):
            return True
        return any(field.initial_value != field.corrected_value for field in self.corrected_value)

    def update(self) -> None:
        for field in self.corrected_value:
            field.update()
        self.initial_value, self.corrected_value = self.corrected_value, []
