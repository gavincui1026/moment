from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.readposts import Like, Comment


# Likes的Pydantic模型
class LikeModel(BaseModel):
    id: int
    post_id: int
    user_id: int

    class Config:
        orm_mode = True


# Comments的Pydantic模型
class CommentModel(BaseModel):
    id: int
    post_id: int
    user_id: int
    content: str
    created_at: datetime
    parent_id: int

    class Config:
        orm_mode = True


# Post的Pydantic模型
class PostModel(BaseModel):
    id: int
    user_id: int
    avatar: str
    nickname: str
    create_time: datetime
    content: str
    pictures: List[str]  # 根据您的JSON列类型进行调整
    likes: List[Like] = []
    comments: List[Comment] = []
    is_liked: bool

    class Config:
        orm_mode = True


class AllPosts(BaseModel):
    total: int
    posts: List[PostModel] = []
