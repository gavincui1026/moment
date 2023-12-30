from fastapi import Depends
from sqlalchemy import select

from app.db.get_db import get_db, get_db2
from app.models.moment import Block, AddonUser


async def uid_to_id(uid: str, db2):
    query = select(AddonUser).where(AddonUser.chat_uid == uid)
    result = await db2.execute(query)
    user = result.scalars().first()
    return user.id


async def is_block(uid: str, friend_uid: str, db2):
    user_id = await uid_to_id(uid, db2)
    friend_id = await uid_to_id(friend_uid, db2)
    query = select(Block).where(Block.user_id == user_id, Block.to_user_id == friend_id)
    result = await db2.execute(query)
    block = result.scalars().first()
    return block
