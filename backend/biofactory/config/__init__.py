from typing import Optional

from pydantic import BaseModel as PydanticBaseModel

from biofactory.config.connection import ConnectionConfig
from biofactory.config.temperature import TemperatureConfig

from .folder import FolderConfig


class Config(PydanticBaseModel):
    class Config:
        use_enum_values = True

    folder: FolderConfig = FolderConfig()
    temperature: TemperatureConfig = TemperatureConfig()
    connection: ConnectionConfig = ConnectionConfig()

    def save(self):
        if self._save_callback:
            self._save_callback()

    def set_save_callback(self, callback):
        self._save_callback = callback


_settings: Optional[Config] = None


def settings(init: Optional[Config] = None) -> Config:
    global _settings
    if _settings is not None:
        if init:
            raise ValueError("Settings Manager already initialized")
    else:
        if init:
            _settings = init
        else:
            raise ValueError("Settings not initialized yet")

    return _settings
