import tomllib
from dataclasses import dataclass


@dataclass(frozen=True)
class DeviceConfig:
    addr: str
    name: str
    packet_header: bytes

@dataclass
class RMQConfig:
    username: str
    password: str
    exchange: str
    q_mongo: str
    vhost: str = '/'

@dataclass(frozen=True)
class Config:
    device: DeviceConfig
    rmq: RMQConfig


def load_config(path: str = "config.toml") -> Config:
    with open(path, "rb") as file:
        raw = tomllib.load(file)

    return Config(
        device=DeviceConfig(
            addr=raw["device"]["addr"],
            name=raw["device"]["name"],
            packet_header=bytes(raw["device"]["packet_header"]),
        ),
        rmq=RMQConfig(
            vhost=raw["rmq"]["vhost"],
            username=raw["rmq"]["username"],
            password=raw["rmq"]["password"],
            exchange=raw["rmq"]["exchange_name"],
            q_mongo=raw["rmq"]["q_mongo"],
        ),
    )