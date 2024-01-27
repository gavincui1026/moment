from pydantic import BaseModel


class Get_SignModel(BaseModel):
    name: str
    md5: str
    thumb: str
    ext: str
    size: int
    width: int
    height: int
    mime: str
    duration: int


class GetSignResponse(BaseModel):
    id: int
    name: str
    path: str
    md5: str
    duration: int
