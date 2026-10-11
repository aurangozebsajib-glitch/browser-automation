
from abc import ABC, abstractmethod
class ProviderAdapter(ABC):
    @abstractmethod
    def submit(self, prompt: str, task_type: str) -> str:
        pass
