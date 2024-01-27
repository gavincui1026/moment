from pydantic import BaseModel
from datetime import datetime
from typing import List


class LikePush(BaseModel):
    post_id: int
    user_id: int
    pictures: List[str]
    content: str
    create_time: datetime
    like_time: str = None

    @property
    def formatted_like_time(self):
        # 返回当前时间的格式化字符串
        return self.like_time or datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    class Config:
        orm_mode = True
        anystr_strip_whitespace = True
        validate_assignment = True

    def __init__(self, **data):
        super().__init__(**data)
        if self.like_time is None:
            self.like_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
