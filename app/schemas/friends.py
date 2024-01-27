from pydantic import BaseModel

from typing import Optional, List

from sqlalchemy import Float


class Follower(BaseModel):
    uid: str
    avatar: str
    nickname: str
    is_followed: bool


class FollowsModel(BaseModel):
    followers: List[Follower]


class Uid(BaseModel):
    uid: str
