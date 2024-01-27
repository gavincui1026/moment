from typing import Optional, List

from pydantic import BaseModel


class AddonUserModel(BaseModel):
    uid: str
    avatar: str
    nickname: str


class BlacklistModel(BaseModel):
    blacklist: Optional[List[AddonUserModel]]
