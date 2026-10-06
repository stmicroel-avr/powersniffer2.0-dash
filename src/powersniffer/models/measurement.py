import json
from uuid import uuid4
from datetime import datetime
from dataclasses import dataclass


@dataclass
class Measurement:
    timestamp: datetime
    value: int
    unit: str

    def to_json(self) -> str:
        return json.dumps({
            'key': str(uuid4()),
            'timestamp': self.timestamp.isoformat(),
            'value': self.value,
            'unit': self.unit,
        })