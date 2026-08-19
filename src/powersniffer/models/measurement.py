from dataclasses import dataclass
from datetime import datetime


@dataclass
class Measurement:
    timestamp: datetime
    value: int
    unit: str
