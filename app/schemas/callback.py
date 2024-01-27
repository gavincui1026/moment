from pydantic import BaseModel


class CallbackModel(BaseModel):
    id: int
    name: str
    path: str
    md5: str
    duration: int
