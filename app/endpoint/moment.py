import json
from typing import List
from collections import defaultdict

import requests
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from app.auth.deps import get_current_user
from app.db.get_db import get_db, get_db2
from app.db.redis.redis_session import get_redis_client
from app.models.moment import Post, Likes, Comments, User, Friends, Block
from app.schemas.friends import Uid
from app.schemas.moment import (
    PostCreate,
    PostLike,
    PostComment,
    Cordination,
    AccurateAddress,
)
from app.schemas.momentpush import LikePush
from app.schemas.mypost import PostModel, CommentModel, LikeModel, AllPosts
from app.schemas.readposts import (
    ReadPost,
    Like,
    Comment,
    UserInfo,
    OneMoment,
    AllMoments,
)
from app.utills.is_block import is_block
import uuid

router = APIRouter()


async def get_user_by_uid(uid, db: AsyncSession):
    query = select(User).where(User.uid == uid)
    result = await db.execute(query)
    user = result.scalars().first()  # 这应该返回一个 User 对象或 None
    return user


async def get_user_by_id(user, db: AsyncSession):
    query = select(User).where(User.id == user)
    result = await db.execute(query)
    user = result.scalars().first()  # 这应该返回一个 User 对象或 None
    return user


async def get_likes(post_ids: List[int], db: AsyncSession) -> dict:
    like_query = select(Likes).where(Likes.post_id.in_(post_ids))
    likes_result = await db.execute(like_query)
    likes = likes_result.scalars().all()
    likes_dict = defaultdict(list)
    for like in likes:
        user_info = UserInfo(
            user_id=like.user.user_id,
            avatar=like.user.avatar,
            nickname=like.user.nickname,
            uid=like.user.uid,
        )
        likes_dict[like.post_id].append(
            Like(id=like.id, post_id=like.post_id, user=user_info)
        )
    return likes_dict


async def get_comments(post_ids: List[int], db: AsyncSession) -> dict:
    comment_query = select(Comments).where(Comments.post_id.in_(post_ids))
    comments_result = await db.execute(comment_query)
    comments = comments_result.scalars().all()
    comments_dict = defaultdict(list)
    for comment in comments:
        user_info = UserInfo(
            user_id=comment.user.user_id,
            avatar=comment.user.avatar,
            nickname=comment.user.nickname,
            uid=comment.user.uid,
        )
        comments_dict[comment.post_id].append(
            Comment(
                id=comment.id,
                post_id=comment.post_id,
                content=comment.content,
                created_at=comment.created_at,
                user=user_info,
                parent_id=comment.parent_id,
            )
        )
    return comments_dict


def uuid_generate():
    return str(uuid.uuid4())


@router.post("/create_post", response_model=PostCreate)
async def create_post(
    post: PostCreate, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)
):
    pictures_data = [str(url) for url in post.pictures] if post.pictures else []
    query = insert(Post).values(
        user_id=user.id,
        content=post.content,
        pictures=pictures_data,
    )
    result = await db.execute(query)
    await db.commit()
    last_record_id = result.inserted_primary_key[0]
    return {**post.model_dump(), "id": last_record_id}


@router.get("/delete_post")
async def delete_post(
    post_id: int, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)
):
    query = Post.__table__.delete().where(Post.user_id == user.id, Post.id == post_id)
    await db.execute(query)
    await db.commit()
    return {"msg": "success"}


@router.post("/like_post")
async def like_post(
    like: PostLike,
    db: AsyncSession = Depends(get_db),
    user=Depends(get_current_user),
    redis=Depends(get_redis_client),
):
    if await Likes.is_liked(user.id, like.post_id, db):
        return {"msg": "请勿重复操作"}
    query = insert(Likes).values(
        post_id=like.post_id,
        user_id=user.id,
    )
    await db.execute(query)
    await db.commit()
    channel = "DB0:Moment"
    post = await Post.get_post(like.post_id, db)
    message = {
        "session_type": 4,
        "chatId": post.user_id,
        "chat_from_id": user.id,
        "moment_event": "like",
        "is_refused": 0,
        "post": LikePush(
            post_id=post.id,
            user_id=user.id,
            pictures=post.pictures,
            content=post.content,
            create_time=post.create_time,
        ).json(),
        "chat_to_id": post.user_id,
        "from_user": UserInfo(
            user_id=user.id, avatar=user.avatar, nickname=user.nickname, uid=user.uid
        ).json(),
        "session_content": "赞了你的动态",
        # "offLinePush": "default",
        "msgid": uuid_generate(),
    }
    message = json.dumps(message)
    redis.publish(channel, message)
    redis.publish("DB0:sendmsg", message)

    return {"msg": "success"}


@router.post("/comment_post")
async def comment_post(
    comment: PostComment,
    db=Depends(get_db),
    user=Depends(get_current_user),
    redis=Depends(get_redis_client),
):
    query = insert(Comments).values(
        post_id=comment.post_id,
        user_id=user.id,
        content=comment.content,
        parent_id=comment.parent_id,
    )
    await db.execute(query)
    await db.commit()
    channel = "DB0:Moment"
    post = await Post.get_post(comment.post_id, db)
    message = {
        "session_type": 4,
        "chatId": post.user_id,
        "chat_from_id": user.id,
        "moment_event": "comment",
        "is_refused": 0,
        "content": comment.content,
        "user": UserInfo(
            user_id=user.id, avatar=user.avatar, nickname=user.nickname, uid=user.uid
        ).json(),
        "post": LikePush(
            post_id=post.id,
            user_id=post.user_id,
            pictures=post.pictures,
            content=post.content,
            create_time=post.create_time,
        ).json(),
        "offLinePush": "default",
        "msgid": uuid_generate(),
    }
    message = json.dumps(message)
    redis.publish(channel, message)
    return {"msg": "success"}


@router.get("/get_friends_posts")
# 使用OneMoment，AllMoments，ReadPost，UserInfo，Like，Comment
async def get_friends_posts(
    user=Depends(get_current_user),
    page: int = 0,
    page_size: int = 5,
    db: AsyncSession = Depends(get_db),
    db2: AsyncSession = Depends(get_db2),
):
    friends = await Friends.get_all_friends(user.id, db)
    friends_id_list = [friend.id for friend in friends]
    all_posts, total = await Post.get_posts(friends_id_list, page, page_size, db)
    return AllMoments(
        total=total,
        posts=[
            OneMoment(
                user=UserInfo(
                    user_id=post.user.id,
                    avatar=post.user.avatar,
                    nickname=post.user.nickname,
                    uid=post.user.uid,
                ),
                post=ReadPost(
                    id=post.id,
                    user_id=post.user_id,
                    create_time=post.create_time,
                    content=post.content,
                    pictures=post.pictures,
                    is_liked=await Likes.is_liked(user.id, post.id, db),
                    likes=[
                        Like(
                            id=like.id,
                            post_id=like.post_id,
                            user=UserInfo(
                                user_id=like.user.id,
                                avatar=like.user.avatar,
                                nickname=like.user.nickname,
                                uid=like.user.uid,
                            ),
                        )
                        for like in post.likes
                    ],
                    comments=[
                        Comment(
                            id=comment.id,
                            post_id=comment.post_id,
                            content=comment.content,
                            created_at=comment.created_at,
                            parent_id=comment.parent_id,
                            user=UserInfo(
                                user_id=comment.user.id,
                                avatar=comment.user.avatar,
                                nickname=comment.user.nickname,
                                uid=comment.user.uid,
                            ),
                        )
                        for comment in post.comments
                    ],
                ),
            )
            for post in all_posts
        ],
    )


@router.get("/get_posts")
async def get_my_posts(
    user=Depends(get_current_user),
    page: int = 0,  # 默认值为第一页
    page_size: int = 5,  # 默认每页大小为5
    db: AsyncSession = Depends(get_db),
):
    total_query = select(func.count()).select_from(Post).where(Post.user_id == user.id)
    total_count = await db.scalar(total_query)
    query = (
        select(Post)
        .options(
            selectinload(Post.likes).selectinload(Likes.user),
            selectinload(Post.comments).selectinload(Comments.user),
        )
        .where(Post.user_id == user.id)
        .order_by(Post.create_time.desc())
        .offset(page * page_size)  # 跳过前面的页数
        .limit(page_size)  # 返回当前页的条目
    )
    my_posts = []
    result = await db.execute(query)
    posts = result.scalars().all()
    for post in posts:
        my_post = PostModel(
            id=post.id,
            user_id=post.user_id,
            avatar=user.avatar,
            nickname=user.nickname,
            create_time=post.create_time,
            content=post.content,
            pictures=post.pictures,
            is_liked=await Likes.is_liked(user.id, post.id, db),
            likes=[
                Like(
                    id=like.id,
                    post_id=like.post_id,
                    user=UserInfo(
                        user_id=like.user_id,
                        avatar=like.user.avatar,
                        nickname=like.user.nickname,
                        uid=like.user.uid,
                    ),
                )
                for like in post.likes
            ],
            comments=[
                Comment(
                    id=comment.id,
                    post_id=comment.post_id,
                    content=comment.content,
                    created_at=comment.created_at,
                    parent_id=comment.parent_id,
                    user=UserInfo(
                        user_id=comment.user_id,
                        avatar=comment.user.avatar,
                        nickname=comment.user.nickname,
                        uid=comment.user.uid,
                    ),
                )
                for comment in post.comments
            ],
        )
        my_posts.append(my_post)
    return AllPosts(total=total_count, posts=my_posts)


@router.get("/get_me", name="获取个人信息")
async def get_me(
    uid: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(User).where(User.uid == uid)
    result = await db.execute(query)
    user = result.scalars().first()
    return {"uid": user.uid, "avatar": user.avatar, "nickname": user.nickname}


@router.post("/get_user_posts", name="获取用户帖子")
async def get_user_posts(
    uid: Uid,
    user=Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    db2: AsyncSession = Depends(get_db2),
    page: int = 0,
    page_size: int = 5,
):
    query = select(User).where(User.uid == uid.uid)
    result = await db.execute(query)
    friend = result.scalars().first()
    if await is_block(user.uid, uid.uid, db2):
        return {"msg": "你已把对方拉黑"}
    elif await is_block(uid.uid, user.uid, db2):
        return {"msg": "对方拉黑了你"}
    all_posts, total = await Post.get_posts([friend.id], page, page_size, db)
    return AllMoments(
        total=total,
        posts=[
            OneMoment(
                user=UserInfo(
                    user_id=post.user.id,
                    avatar=post.user.avatar,
                    nickname=post.user.nickname,
                    uid=post.user.uid,
                ),
                post=ReadPost(
                    id=post.id,
                    user_id=post.user_id,
                    create_time=post.create_time,
                    content=post.content,
                    pictures=post.pictures,
                    is_liked=await Likes.is_liked(user.id, post.id, db),
                    likes=[
                        Like(
                            id=like.id,
                            post_id=like.post_id,
                            user=UserInfo(
                                user_id=like.user.id,
                                avatar=like.user.avatar,
                                nickname=like.user.nickname,
                                uid=like.user.uid,
                            ),
                        )
                        for like in post.likes
                    ],
                    comments=[
                        Comment(
                            id=comment.id,
                            post_id=comment.post_id,
                            content=comment.content,
                            created_at=comment.created_at,
                            parent_id=comment.parent_id,
                            user=UserInfo(
                                user_id=comment.user.id,
                                avatar=comment.user.avatar,
                                nickname=comment.user.nickname,
                                uid=comment.user.uid,
                            ),
                        )
                        for comment in post.comments
                    ],
                ),
            )
            for post in all_posts
        ],
    )


@router.post("/is_blocked")
async def is_blocked(
    uid: Uid,
    user=Depends(get_current_user),
    db2: AsyncSession = Depends(get_db2),
):
    if await is_block(user.uid, uid.uid, db2):
        return {"msg": "你已把对方拉黑"}
    elif await is_block(uid.uid, user.uid, db2):
        return {"msg": "对方拉黑了你"}
    else:
        return {"msg": "ok"}


@router.post("/get_address")
def get_address(
    cordination: Cordination,
):
    google_api_key = "AIzaSyATQOnwcb1OO9Yaz271MbmRjzvae7IdCmU"
    url = f"https://maps.googleapis.com/maps/api/geocode/json?latlng={cordination.lat},{cordination.lng}&key={google_api_key}"
    response = requests.get(url)
    city = None
    if response.status_code == 200:  # 打印整个响应内容
        results = response.json().get("results", [])
        if results:
            for component in results[0].get("address_components", []):
                if "locality" in component.get("types", []):
                    return {"city": component.get("long_name")}
    else:
        print(f"Error: {response.status_code}")
    return None


@router.post("/get_accurate_addresses")
def get_accurate_addresses(addy: AccurateAddress):
    google_api_key = "AIzaSyB-7Xf6FzZL3lqJp2l6vQXJvPQ7U7y1FQY"
    url = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
    params = {
        "input": addy.keyword,
        "types": "address",
        "location": f"{addy.lat},{addy.lng}",
        "radius": 10000,
        "key": google_api_key,
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
