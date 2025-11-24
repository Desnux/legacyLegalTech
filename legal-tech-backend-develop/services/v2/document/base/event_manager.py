from abc import ABC

from models.sql import Case


class BaseEventManager(ABC):
    """Base class for all document event managers."""
    def __init__(self, case: Case) -> None:
        self.case = case
