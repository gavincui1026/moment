from pydantic import BaseModel

from typing import Optional, List


class Follower(BaseModel):
    uid: str
    avatar: str
    nickname: str
    is_followed: bool


class FollowsModel(BaseModel):
    followers: List[Follower]
