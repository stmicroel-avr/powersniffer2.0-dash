from typing import Protocol

class JsonSerializableEvent(Protocol):
    def to_json(self) -> str:
        """
        Object should be serializable to JSON
        :return: str
        """
        ...