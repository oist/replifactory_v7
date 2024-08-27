from typing import Optional

from pydantic import BaseModel as PydanticBaseModel


class FolderConfig(PydanticBaseModel):
    logs: Optional[str] = None
    """Absolute path where to store logs. Defaults to the `logs` folder in Replifactory's base folder."""

    experiments: Optional[str] = None
    """Absolute path where to store experiments data. Defaults to the `experiments` folder in Replifactory's base folder."""
