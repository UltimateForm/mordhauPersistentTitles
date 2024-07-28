from dataclasses import dataclass, field
import json
import os
from dacite import from_dict
import logger


@dataclass
class Config:
    tags: dict[str, str]
    salutes: dict[str, str]
    playtime_tags: dict[str, str] | None = field(default_factory=dict)
    rename: dict[str, str] | None = field(default_factory=dict)
    tag_format: str = "[{0}]"
    salute_timer: int = 2


@dataclass
class SessionEvent:
    playfab_id: str
    minutes: int


def load_config(path: str = "./persist/config.json") -> Config:
    if not os.path.exists(path):
        return Config({}, {})
    json_data: dict = None
    with open(path, "r", encoding="utf8") as config_file:
        json_data = json.loads(config_file.read())
    config_data = from_dict(data_class=Config, data=json_data)
    return config_data


def save_config(config: Config, path: str = "./persist/config.json"):
    with open(path, "w", encoding="utf8") as config_file:
        json.dump(config.__dict__, config_file, indent=2)


if __name__ == "__main__":
    logger.use_date_time_logger()
    confg = load_config()
    logger.info(confg)
