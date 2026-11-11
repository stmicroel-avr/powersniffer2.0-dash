import json
from uuid import uuid4
from datetime import datetime

from pydantic import BaseModel, Field


class Measurement(BaseModel):
    """Producer dto for any metrics"""
    timestamp: datetime
    value: int
    unit: str
    key: str = Field(default_factory=lambda: str(uuid4()))

    def to_json(self) -> str:
        return json.dumps({
            'key': self.key,
            'timestamp': self.timestamp.isoformat(),
            'value': self.value,
            'unit': self.unit,
        })
