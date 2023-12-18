from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.get_db import get_db
from app.models.token import Token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
async def verify_token(token: str, db: AsyncSession = Depends(get_db)):
    db_token = await db.execute(
        select(Token).where(Token.token == token)
    )
    db_token = db_token.scalars().first()
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    return db_token.uid