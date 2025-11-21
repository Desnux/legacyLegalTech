from abc import ABC, abstractmethod

from .models import OutputBaseModel


class BaseSender(ABC):
    """Base class for all document senders."""
    @abstractmethod
    def send(self) -> OutputBaseModel:
        """Subclasses must implement this method to send a structured input."""
        pass
