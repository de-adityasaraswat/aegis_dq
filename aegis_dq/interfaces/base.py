from abc import ABC, abstractmethod
from typing import Dict, Any


class MetadataSinkInterface(ABC):
    """The blueprint for how results must be persisted."""

    @abstractmethod
    def write_results(self, table_name: str, results: Dict[str, Any]) -> None:
        pass


class AlertManagerInterface(ABC):
    """The blueprint for how alerts must be sent."""

    @abstractmethod
    def notify(self, message: str, level: str) -> None:
        pass
