import logging


class NotificationDispatcher:
    def __init__(self, *args):
        self.handlers = args
        self.logger = logging.getLogger(__name__)

    def handle(self, ch, packet):
        """
        Handle all notifications
        :return:
        """
        self.logger.info(f"Received data packet {packet}")

        if not len(self.handlers):
            self.logger.warning(f"No handlers found")
            return

        for handler in self.handlers:
            handler.handle()
