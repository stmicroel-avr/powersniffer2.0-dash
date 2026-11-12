from datetime import datetime
from pydantic import BaseModel, model_validator


class MeasurementParams(BaseModel):
    date_from: datetime
    date_to: datetime | None = None

    @model_validator(mode='after')
    def check_date_range(self):
        if self.date_to and self.date_from > self.date_to:
            raise ValueError('Date from must be before date')
        return self

class MeasurementItemResponse(BaseModel):
    key: str
    value: float
    timestamp: datetime

class MeasurementsResponse(BaseModel):
    items: list[MeasurementItemResponse]
