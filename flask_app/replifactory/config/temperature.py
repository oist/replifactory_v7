
from pydantic import BaseModel as PydanticBaseModel


class TemperatureConfig(PydanticBaseModel):

    cutoff: int = 30
    """Cut off time for the temperature data, in minutes."""
