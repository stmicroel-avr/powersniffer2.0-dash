from datetime import datetime
from pydantic import BaseModel, model_validator


class MeasurementQueryParams(BaseModel):
    date_from: datetime
    date_to: datetime | None = None

    @model_validator(mode='after')
    def check_date_range(self):
        if self.date_to and self.date_from > self.date_to:
            raise ValueError('Date from must be before date')
        return self