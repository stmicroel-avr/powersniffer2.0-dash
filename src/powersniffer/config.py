from dataclasses import dataclass
import tomllib


@dataclass(frozen=True)
class DeviceConfig:
    addr: str
    name: str
    packet_header: bytes


@dataclass(frozen=True)
class Config:
    device: DeviceConfig


def load_config(path: str = "config.local.toml") -> Config:
    with open(path, "rb") as file:
        raw = tomllib.load(file)

    return Config(
        device=DeviceConfig(
            addr=raw["device"]["addr"],
            name=raw["device"]["name"],
            packet_header=bytes(raw["device"]["packet_header"]),
        ),
    )