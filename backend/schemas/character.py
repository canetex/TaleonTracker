from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class CharacterHistoryBase(BaseModel):
    level: int
    experience: float
    deaths: int
    timestamp: datetime

class CharacterHistoryCreate(CharacterHistoryBase):
    pass

class CharacterHistory(CharacterHistoryBase):
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
    created_at: datetime
    updated_at: datetime
    history: List[CharacterHistory]

    class Config:
        from_attributes = True
