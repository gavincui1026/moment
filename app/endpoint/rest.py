from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user, get_current_user2
from app.db.get_db import get_db2, get_db
from app.models.moment import User, Friends

router = APIRouter()


@router.get("/user_follow", name="获取用户关注列表")
async def user_follow(uid: int, db=Depends(get_db)):
    uid = "user-" + str(uid)
    queue = select(User).where(User.uid == uid)
    user = await db.execute(queue)
    user = user.scalars().first()
    query = select(Friends).where(Friends.from_id == user.id)
    friends = await db.execute(query)
    following = friends.scalars().all()
    query = select(Friends).where(Friends.to_id == user.id)
    friends = await db.execute(query)
    follower = friends.scalars().all()
    return {"following": len(following), "follower": len(follower)}
