from datetime import datetime

from fastapi import APIRouter, Depends
from sqlalchemy import select, insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user, get_current_user2
from app.db.get_db import get_db2, get_db
from app.utills.get_sign import get_callback, validator
from app.schemas.get_sign import Get_SignModel, GetSignResponse
from app.models.token import Upload

route = APIRouter()


def get_file_url(path: str) -> str:
    return f"https://ams1.vultrobjects.com/moment/{path}"


@route.post("/get_oss_sign", name="获取oss签名", response_model=GetSignResponse)
async def get_oss_sign(
    get_sign: Get_SignModel,
    user=Depends(get_current_user2),
    db2: AsyncSession = Depends(get_db2),
):
    await validator(get_sign)
    callback = await get_callback(get_sign.md5, db2)
    if callback:
        return GetSignResponse(
            id=callback.id,
            name=callback.name,
            path=callback.path,
            md5=callback.md5,
            duration=callback.duration,
        )
    query = insert(Upload).values(
        uid=user.id,
        name=get_sign.name,
        module="api",
        path=get_file_url(get_sign.md5 + "." + get_sign.ext),
        thumb=get_sign.thumb,
        mime=get_sign.mime,
        ext=get_sign.ext,
        size=get_sign.size,
        md5=get_sign.md5,
        driver="vultross",
        width=get_sign.width,
        height=get_sign.height,
        duration=get_sign.duration,
        key="184S0F7JDAMJYYY4IOPS",
    )
    await db2.execute(query)
    await db2.commit()
    callback = await get_callback(get_sign.md5, db2)
    return GetSignResponse(
        id=callback.id,
        name=callback.name,
        path=callback.path,
        md5=callback.md5,
        duration=callback.duration,
    )


@route.post("/im_get_oss_sign", name="获取oss签名", response_model=GetSignResponse)
async def im_get_oss_sign(
    get_sign: Get_SignModel,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await validator(get_sign)
    callback = await get_callback(get_sign.md5, db)
    if callback:
        return GetSignResponse(
            id=callback.id,
            name=callback.name,
            path=callback.path,
            md5=callback.md5,
            duration=callback.duration,
        )
    query = insert(Upload).values(
        uid=user.id,
        name=get_sign.name,
        module="api",
        path=get_file_url(get_sign.md5 + "." + get_sign.ext),
        thumb=get_sign.thumb,
        mime=get_sign.mime,
        ext=get_sign.ext,
        size=get_sign.size,
        md5=get_sign.md5,
        driver="vultross",
        width=get_sign.width,
        height=get_sign.height,
        duration=get_sign.duration,
        key="184S0F7JDAMJYYY4IOPS",
    )
    await db.execute(query)
    await db.commit()
    callback = await get_callback(get_sign.md5, db)
    return GetSignResponse(
        id=callback.id,
        name=callback.name,
        path=callback.path,
        md5=callback.md5,
        duration=callback.duration,
    )
