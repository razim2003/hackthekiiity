from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CatCreate(BaseModel):
    status: str
    location: str
    description: str
    owner_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None

class CatResponse(BaseModel):
    id: str
    status: str
    location: str
    description: str
    image_url: str
    owner_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    created_at: datetime

class SimilarCatResponse(BaseModel):
    cat_id: str
    image_url: str
    status: str
    location: str
    description: str
    owner_name: Optional[str] = None
    contact_phone: Optional[str] = None
    contact_email: Optional[str] = None
    similarity_score: float
