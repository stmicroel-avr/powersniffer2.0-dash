import logging
from datetime import datetime, timedelta
from collections.abc import Generator

from powersniffer.models.measurement import Measurement


class PacketParser:
    def __init__(self, data_header: bytes, series_length: int = 5):
        self.header = data_header
        self.series_length = series_length
        self.logger: logging.Logger = logging.getLogger(__name__)

    def _calc_checksum(self, data: bytes) -> int:
        """
        Calculate checksum (single 8 bits)
        :param data:
        :return:
        """
        return sum(data) & 0xFF

    def _extract_payload_length(self, data: bytes) -> int:
        """
        Extract payload length from next byte after header prefix
        :param data:
        :return:
        """
        return data[len(self.header)]

    def _extract_chunk_items(self, ts: datetime, data: bytes) -> list[Measurement]:
        """
        Get normalized values from raw chunk
        :param data:
        :return:
        """
        vcc = Measurement(
            timestamp=ts,
            value=int.from_bytes(data[0:2], byteorder="little"),
            unit='vcc'
        )

        voltage = Measurement(
            timestamp=ts,
            value=int.from_bytes(data[2:4], byteorder="little"),
            unit='V'
        )

        current = Measurement(
            timestamp=ts,
            value=int.from_bytes(data[4:8], byteorder="little"),
            unit='A'
        )

        return [vcc, voltage, current]

    def check(self, data: bytes) -> bool:
        """
        Check if a data is valid
        :param data:
        :return:
        """
        data_length = len(data)
        head_length = len(self.header) + 1
        if data_length < head_length:
            self.logger.warning(f"Corrupt packet {data}")
            return False

        payload_length = self._extract_payload_length(data)
        if data_length != (head_length + payload_length + 1):
            self.logger.warning(f"Corrupt packet {data}. Incorrect payload length. Expected {payload_length}")
            return False

        if self.header != data[0:len(self.header)]:
            self.logger.warning(f"Received wrong packet header. Expected header: {data[0:len(self.header)]}")
            return False

        expected_checksum = data[-1]
        checksum = self._calc_checksum(data[3:-1])

        if expected_checksum != checksum:
            self.logger.warning(f"Received wrong checksum. Expected {expected_checksum}, got {checksum}")
            return False

        return True

    def get_series_chunk(self, data: bytes) -> Generator[bytes]:
        """
        Get series chunk
        :param data: Payload
        :return:
        """
        i = 0
        measurement_length = int(len(data) / self.series_length)
        while i < self.series_length:
            start_pos = i * measurement_length
            yield data[start_pos:start_pos + measurement_length]
            i += 1


    def extract(self, data: bytes) -> list[Measurement]:
        """
        Extract parse and normilize measurements
        :param data: Data
        :return:
        """
        # Heuristic time of events
        touch_ts = (datetime.now() - timedelta(seconds=1)).replace(microsecond=0)
        self.logger.info(f"Received {len(data)} bytes")
        if not self.check(data=data):
            raise ValueError(f"Invalid packet {data}")

        raw_payload = data[3:-1]

        self.logger.debug(f"Payload bytes {raw_payload}")

        measurements = []
        for seq, chunk in enumerate(self.get_series_chunk(data=raw_payload)):
            measurements += self._extract_chunk_items(touch_ts, chunk)
            touch_ts += timedelta(microseconds=200000)

        return measurements


