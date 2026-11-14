from starlette.websockets import WebSocket, WebSocketDisconnect

from powersniffer.logger import get_app_logger


class WebSocketPool:
    def __init__(self):
        self.pool = set()
        self.logger = get_app_logger(__name__)

    def register(self, ws: WebSocket) -> None:
        """
        Register a new WebSocket connection
        :param ws: WebSocket instance
        :return: None
        """
        self.pool.add(ws)

    def unregister(self, ws: WebSocket) -> None:
        self.pool.discard(ws)

    async def broadcast(self, raw_payload: dict) -> int:
        """
        Broadcast all WebSocket connections
        :return: Number of successful sends
        """
        sent = 0
        for ws in self.pool.copy():
            try:
                await ws.send_json(raw_payload)
                sent += 1
            except WebSocketDisconnect:
                self.unregister(ws)
                self.logger.debug('WebSocket disconnected: %s', ws)

        return sent