import uvicorn
from fastapi import FastAPI, Query
from typing_extensions import Annotated

from powersniffer.web.dto import MeasurementQueryParams

app = FastAPI()

app.frontend("/", directory="dist")

@app.get("/api/v1/measurements")
async def get_measurements(filter_query: Annotated[MeasurementQueryParams, Query()]):
    return filter_query


def run():
    uvicorn.run(app, host="0.0.0.0", port=8001)