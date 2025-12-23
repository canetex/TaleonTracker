from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ServerStatsBase(BaseModel):
    world: str
    total_experience: float
    active_characters: int

class ServerStatsCreate(ServerStatsBase):
    pass

class ServerStatsResponse(ServerStatsBase):
    id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

