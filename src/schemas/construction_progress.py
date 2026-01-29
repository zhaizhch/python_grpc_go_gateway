from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ConstructionProgressBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    type: str
    creator: str

class ConstructionProgressCreate(ConstructionProgressBase):
    pass

class ConstructionProgressUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    progress: Optional[str] = None

class ConstructionProgressRead(ConstructionProgressBase):
    id: str
    progress: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
