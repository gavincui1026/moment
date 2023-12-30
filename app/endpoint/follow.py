from fastapi import APIRouter, Depends
from sqlalchemy import insert, select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.deps import get_current_user
from app.db.get_db import get_db, get_db2
from app.models.moment import Friends, User, Block, AddonUser
from app.schemas.friends import Follower, FollowsModel
from app.schemas.blacklist import BlacklistModel, AddonUserModel
from app.utills.is_block import is_block, uid_to_id

router = APIRouter()


async def get_user_by_uid(uid: str, db: AsyncSession):
    query = select(AddonUser).where(AddonUser.chat_uid == uid)
    result = await db.execute(query)
    user = result.scalars().first()
    return user


async def is_followed(friend_id: int, user_id: int, db: AsyncSession):
    query = select(Friends).where(
        Friends.from_id == user_id, Friends.to_id == friend_id
    )
    result = await db.execute(query)
    friend = result.scalars().first()
    return friend is not None


@router.post("/follow", name="关注用户")
async def follow(
    uid: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    friend = await get_user_by_uid(uid, db)
    if friend:
        query = insert(Friends).values(to_id=user.id, from_id=friend.id)
        await db.execute(query)
        await db.commit()
        return {"msg": "关注成功"}
    else:
        return {"msg": "用户不存在"}


@router.post("/unfollow", name="取消关注")
async def unfollow(
    uid: str, user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    friend = await get_user_by_uid(uid, db)
    if friend:
        query = delete(Friends).where(
            Friends.to_id == user.id, Friends.from_id == friend.id
        )
        await db.execute(query)
        await db.commit()
        return {"msg": "取消关注成功"}
    else:
        return {"msg": "用户不存在"}


@router.get(
    "/followers",
    response_model=FollowsModel,
    name="获取粉丝列表",
)
async def get_followers(
    user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    query = select(Friends).where(Friends.to_id == user.id)
    result = await db.execute(query)
    friends = result.scalars().all()
    friends_ids = [friend.to_id for friend in friends]
    query = select(User).where(User.id.in_(friends_ids))
    result = await db.execute(query)
    friends = result.scalars().all()
    followers = []
    for friend in friends:
        followers.append(
            Follower(
                uid=friend.uid,
                avatar=friend.avatar,
                nickname=friend.nickname,
                is_followed=is_followed(friend.id, user.id, db),
            )
        )
    return FollowsModel(followers=followers)


@router.get(
    "/follows",
    response_model=FollowsModel,
    name="获取关注列表",
)
async def get_follows(
    user=Depends(get_current_user), db: AsyncSession = Depends(get_db)
):
    query = select(Friends).where(Friends.from_id == user.id)
    result = await db.execute(query)
    friends = result.scalars().all()
    friends_ids = [friend.to_id for friend in friends]
    query = select(User).where(User.id.in_(friends_ids))
    result = await db.execute(query)
    friends = result.scalars().all()
    followers = []
    for friend in friends:
        followers.append(
            Follower(
                uid=friend.uid,
                avatar=friend.avatar,
                nickname=friend.nickname,
                is_followed=await is_followed(friend.id, user.id, db),
            )
        )
    return FollowsModel(followers=followers)


@router.post("/blacklist", name="拉黑用户")
async def blacklist(
    uid: str,
    user=Depends(get_current_user),
    db2: AsyncSession = Depends(get_db2),
):
    friend = await get_user_by_uid(uid, db2)
    me = await get_user_by_uid(user.uid, db2)
    query = insert(Block).values(user_id=me.id, to_user_id=friend.id)
    await db2.execute(query)
    await db2.commit()
    return {"msg": "拉黑成功"}


@router.get("/get_blacklist", name="获取黑名单", response_model=BlacklistModel)
async def get_blacklist(
    user=Depends(get_current_user), db2: AsyncSession = Depends(get_db2)
):
    addon_user = await get_user_by_uid(user.uid, db2)
    query = select(Block).where(Block.user_id == addon_user.id)
    result = await db2.execute(query)
    blocks = result.scalars().all()
    blocks_ids = [block.to_id for block in blocks]
    query = select(AddonUser).where(AddonUser.id.in_(blocks_ids))
    result = await db2.execute(query)
    blocks = result.scalars().all()
    blacklist = []
    for block in blocks:
        blacklist.append(
            AddonUser(
                uid=block.chat_uid,
                avatar=block.head_img,
                nickname=block.user_nickname,
            )
        )
    return BlacklistModel(blacklist=blacklist)
