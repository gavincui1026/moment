from sqlalchemy.ext.asyncio import AsyncSession
from app.models.token import Token

class TokenOperations:
    @staticmethod
    async def check_user_token(uid: str, token: str, db: AsyncSession) -> bool:
        result = await db.query(Token).filter(
            Token.uid == uid,
            Token.token == token
        ).first()
        return result is not None

