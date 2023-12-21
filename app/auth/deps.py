from fastapi import Header, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.token import Token
from app.db.get_db import get_db
from app.models.moment import User


async def verify_token(uid: str, token: str, db: AsyncSession) -> bool:
    result = select(Token).where(Token.uid == uid, Token.token == token)
    result = await db.execute(result)
    result = result.scalars().first()
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
