import logging
from collections.abc import Generator

from powersniffer.models.measurement import Measurement


class PacketParser:
    def __init__(self, packet_header: bytes, series_length: int = 5,):
        self.header = packet_header
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

    def _extract_payload(self, data: bytes) -> bytes:


    def check(self, packet: bytes) -> bool:
        """
        Check if a packet is valid
        :param packet:
        :return:
        """
        packet_length = len(packet)
        head_length = len(self.header) + 1
        if packet_length < head_length:
            self.logger.warning(f"Corrupt packet {packet}")
            return False

        payload_length = self._extract_payload_length(packet)
        if packet_length != (head_length + payload_length + 1):
            self.logger.warning(f"Corrupt packet {packet}. Incorrect payload length. Expected {payload_length}")
            return False

        if self.header != packet[0:len(self.header)]:
            self.logger.warning(f"Received wrong packet header. Expected header: {packet[0:len(self.header)]}")
            return False

        expected_checksum = packet[-1]
        checksum = self._calc_checksum(packet[3:-1])

        if expected_checksum != checksum:
            self.logger.warning(f"Received wrong checksum. Expected {expected_checksum}, got {checksum}")
            return False

        return True

    def get_series_chunk(self, payload: bytes) -> Generator[bytes]:
        i = 0
        measurement_length = int(len(payload) / self.series_length)
        while i < self.series_length:
            start_pos = i * measurement_length
            yield payload[start_pos:start_pos + measurement_length]
            i += 1


    def parse(self, data: bytes) -> list[Measurement]:
        self.logger.info(f"Received {len(data)} bytes")
        if not self.check(packet=data):
            raise ValueError(f"Invalid packet {data}")


        return []


