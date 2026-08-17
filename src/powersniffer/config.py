from dataclasses import dataclass
import tomllib


@dataclass(frozen=True)
class DeviceConfig:
    uid: str


@dataclass(frozen=True)
class Config:
    device: DeviceConfig


def load_config(path: str = "config.toml") -> Config:
    with open(path, "rb") as file:
        raw = tomllib.load(file)

    return Config(
        device=DeviceConfig(
            uid=raw["device"]["uid"],
        ),
    )