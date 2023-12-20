from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, HttpUrl


class PostCreate(BaseModel):
    user_id: int
    content: str
    pictures: Optional[List[HttpUrl]] = None
class PostLike(BaseModel):
    post_id: int
    user_id: int
class PostComment(BaseModel):
    post_id: int
    user_id: int
    content: str
    parent_id: int
