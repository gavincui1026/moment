from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl


class PostCreate(BaseModel):
    content: str
    pictures: Optional[List[HttpUrl]] = None


class PostLike(BaseModel):
    post_id: int


class PostComment(BaseModel):
    post_id: int
    content: str
    parent_id: int


class Cordination(BaseModel):
    lat: float
    lng: float


class AccurateAddress(BaseModel):
    address: str
    lat: float
    lng: float
