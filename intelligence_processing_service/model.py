from datetime import datetime
from pydantic import BaseModel, Field, field_validator

SIGNAL_TYPES: list[str] = ["SIGINT", "VISINT", "HUMINT"]


class IntelMessage(BaseModel):
    timestamp: datetime
    signal_id: str
    entity_id: str
    reported_lat: float = Field(ge=-90.0, le=90.0)
    reported_lon: float = Field(ge=-180.0, le=180.0)
    signal_type: str
    priority_level: int

    @classmethod
    @field_validator('signal_type')
    def check_signal_type(cls, value):
        if value not in SIGNAL_TYPES:
            raise ValueError(f'signal_type must be on of those: {" ,".join(SIGNAL_TYPES)}')
        return value

    @classmethod
    @field_validator('priority_level')
    def check_level(cls, value):
        if not 1 <= value <= 5 or value != 99:
            raise ValueError(f'priority level must be between 1-5 or 99')
        return value
