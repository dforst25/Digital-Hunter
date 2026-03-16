from datetime import datetime
from pydantic import BaseModel, field_validator

DAMAGE_RESULTS: list[str] = ["destroyed", "damaged", "no_damage"]


class DamageMessage(BaseModel):
    timestamp: datetime
    attack_id: str
    entity_id: str
    result: str

    @classmethod
    @field_validator('result')
    def check_signal_type(cls, value):
        if value not in DAMAGE_RESULTS:
            raise ValueError(f'damage_results must be on of those: {" ,".join(DAMAGE_RESULTS)}')
        return value
