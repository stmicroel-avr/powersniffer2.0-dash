import uvicorn
from fastapi import FastAPI, Query, Depends
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from typing_extensions import Annotated
from contextlib import asynccontextmanager

from powersniffer.config import load_config
from powersniffer.web.dependencies import get_db
from powersniffer.web.dto import MeasurementQueryParams

@asynccontextmanager
async def lifespan(app: FastAPI):
    config = load_config().mongo
    client = AsyncMongoClient(
        host="localhost",
        port=27017,
        username=config.username,
        password=config.password,
        minPoolSize=1,
        authSource=config.dbname,
    )

    db = AsyncDatabase(client, config.dbname)
    await db.command('ping')
    app.state.db = db

    try:
        yield
    finally:
        await client.close()


app = FastAPI(lifespan=lifespan)

app.frontend("/", directory="dist")

@app.get("/api/v1/measurements")
async def get_measurements(
        filter_query: Annotated[MeasurementQueryParams, Query()],
        db: Annotated[AsyncDatabase, Depends(get_db)]
):
    return await db.command("ping")


def run():
    uvicorn.run(app, host="0.0.0.0", port=8001)