from fastapi import Header, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.token import Token, AddonToken
from app.db.get_db import get_db, get_db2
from app.models.moment import User, AddonUser


async def verify_token(uid: str, token: str, db: AsyncSession) -> bool:
    result = select(Token).where(Token.uid == uid, Token.token == token)
    result = await db.execute(result)
    result = result.scalars().first()
    if not result:
        return None
    user = select(User).where(result.uid == User.uid)
    user = await db.execute(user)
    user = user.scalars().first()
    return user


async def get_current_user(
    api_token: str = Header(convert_underscores=False),
    uid: str = Header(...),
    db: AsyncSession = Depends(get_db),
):
    user = await verify_token(uid, api_token, db)
    if user:
        return user
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")


async def verify_token2(apptoken: str, db: AsyncSession):
    result = select(AddonToken).where(AddonToken.apptoken == apptoken)
    result = await db.execute(result)
    result = result.scalars().first()
    if not result:
        return None
    user = select(AddonUser).where(result.uid == AddonUser.id)
    user = await db.execute(user)
    user = user.scalars().first()
    return user


async def get_current_user2(
    apptoken: str = Header(convert_underscores=False),
    db: AsyncSession = Depends(get_db2),
):
    user = await verify_token2(apptoken, db)
    if user:
        return user
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")
