from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
class UserInfo(BaseModel):
    user_id: int
    avatar: str
    nickname: str

class Like(BaseModel):
    id: int
    post_id: int
    user: UserInfo

class Comment(BaseModel):
    id: int
    post_id: int
    content: str
    created_at: datetime
    user: UserInfo
    parent_id: int

class ReadPost(BaseModel):
    id: int
    user_id: int
    create_time: datetime
    content: str
    pictures: List[str]
    likes: List[Like] = []
    comments: List[Comment] = []
class OneMoment(BaseModel):
    user: UserInfo
    post: ReadPost


