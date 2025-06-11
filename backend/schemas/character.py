from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CharacterBase(BaseModel):
    name: str

class CharacterCreate(CharacterBase):
    pass

class CharacterResponse(CharacterBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CharacterHistoryBase(BaseModel):
    level: int
    experience: float
    deaths: int
    timestamp: datetime

class CharacterHistoryResponse(CharacterHistoryBase):
    id: int
    character_id: int

    class Config:
        from_attributes = True 