from pydantic import BaseModel as PydanticBaseModel


class ConnectionConfig(PydanticBaseModel):

    device_address: str = None
    """Path to device in /dev/..."""

    autoconnect: bool = False
    """Connect to device after server started"""
