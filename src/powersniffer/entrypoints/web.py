import time
import socket
import uvicorn
from fastapi import FastAPI, Query, Depends, WebSocket, WebSocketDisconnect
from pymongo import AsyncMongoClient
from pymongo.asynchronous.database import AsyncDatabase
from typing_extensions import Annotated
from contextlib import asynccontextmanager

from powersniffer.config import load_config
from powersniffer.logger import get_app_logger
from powersniffer.queue_client import QueueClient
from powersniffer.web.dependencies import get_db
from powersniffer.web.dto import MeasurementParams, MeasurementsResponse
from powersniffer.web.queries import find_measurements
from powersniffer.web.websocket import WebSocketPool
from powersniffer.web.ws_event_handler import WebSocketEventHandler

logger = get_app_logger(__name__)

@asynccontextmanager
async def lifespan(engine: FastAPI):
    logger.info("Starting lifespan")
    config = load_config()

    # Websocket
    logger.info("Create websocket pool..")
    engine.state.websocket_pool = WebSocketPool()

    # MongoDB connect
    logger.info("Starting mongo..")
    mongo = AsyncMongoClient(
        host="localhost",
        port=27017,
        minPoolSize=1,
        username=config.mongo.username,
        password=config.mongo.password,
        authSource=config.mongo.dbname,
    )
    db = AsyncDatabase(mongo, config.mongo.dbname)
    await db.command('ping')
    engine.state.db = db

    # RabbitMQ connect
    processor = WebSocketEventHandler(engine.state.websocket_pool)
    engine.state.rmq = QueueClient(config.rmq)
    await engine.state.rmq.start()
    await engine.state.rmq.register_consumer(config.rmq_queue.q_ws, processor.handle)

    try:
        logger.info("App state initialized")
        yield
    finally:
        await mongo.close()
        await engine.state.rmq.stop()

app = FastAPI(lifespan=lifespan)
app.frontend("/", directory="dist")

@app.get("/api/v1/measurements/{unit}", response_model=MeasurementsResponse)
async def get_measurements(unit: str, query: Annotated[MeasurementParams, Query()], db: Annotated[AsyncDatabase, Depends(get_db)]):
    return MeasurementsResponse(items=await find_measurements(db, unit, query))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    app.state.websocket_pool.register(websocket)
    try:
        await websocket.send_json({"msg": "WebSocket alive"})
        while True: await websocket.receive_text()
    except WebSocketDisconnect: pass
    finally:
        app.state.websocket_pool.unregister(websocket)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

def wait_for_port(host: str, port: int) -> None:
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.bind((host, port))
                return
            except OSError as e:
                if e.errno != 98:  # EADDRINUSE
                    raise

        logger.warning(f"Port {port} is busy, waiting...")
        time.sleep(0.5)


def run():
    wait_for_port(host="localhost", port=8001)
    uvicorn.run(app, host="0.0.0.0", port=8001)