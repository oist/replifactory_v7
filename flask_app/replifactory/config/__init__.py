from pydantic import BaseModel as PydanticBaseModel
from flask_app.replifactory.config.connection import ConnectionConfig
from flask_app.replifactory.config.temperature import TemperatureConfig

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


_settings: Config = None


def settings(init=None):
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
