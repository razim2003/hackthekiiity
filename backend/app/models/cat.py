from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class CatCreate(BaseModel):
    status: str
    location: str
    description: str

class CatResponse(BaseModel):
    id: str
    status: str
    location: str
    description: str
    image_url: str
    created_at: datetime

class SimilarCatResponse(BaseModel):
    cat_id: str
    image_url: str
    similarity_score: float
