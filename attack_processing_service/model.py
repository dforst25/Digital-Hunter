from datetime import datetime
from pydantic import BaseModel


class AttackMessage(BaseModel):
    timestamp: datetime
    attack_id: str
    entity_id: str
    weapon_type: str
