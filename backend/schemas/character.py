from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class CharacterHistoryBase(BaseModel):
    level: int
    experience: int
    timestamp: datetime

class CharacterHistoryResponse(CharacterHistoryBase):
    id: int
    character_id: int

    class Config:
        from_attributes = True

class CharacterBase(BaseModel):
    name: str
    level: int
    vocation: str
    world: str

class CharacterCreate(CharacterBase):
    pass

class CharacterResponse(CharacterBase):
    id: int
    last_updated: datetime
    history: Optional[List[CharacterHistoryResponse]] = []

    class Config:
        from_attributes = True
