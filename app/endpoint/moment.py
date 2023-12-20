from collections import defaultdict
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import selectinload
from fastapi import APIRouter, Depends
from sqlalchemy import select, or_
from sqlalchemy.dialects.mysql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.moment import Post, Likes, Comments, User, Friends
from app.schemas.moment import PostCreate, PostLike, PostComment
from app.schemas.mypost import PostModel,CommentModel,LikeModel
from app.schemas.readposts import ReadPost, Like, Comment, UserInfo,OneMoment
from app.db.get_db import get_db
router = APIRouter()

async def get_user_by_id(user_id: int, db: AsyncSession):
    query = select(User).where(User.user_id == user_id)
    result = await db.execute(query)
    user = result.scalars().first()  # 这应该返回一个 User 对象或 None
    return user
async def get_likes(post_ids: List[int], db: AsyncSession) -> dict:
    like_query = select(Likes).where(Likes.post_id.in_(post_ids))
    likes_result = await db.execute(like_query)
    likes = likes_result.scalars().all()
    likes_dict = defaultdict(list)
    for like in likes:
        user_info = UserInfo(user_id=like.user.user_id, avatar=like.user.avatar, nickname=like.user.nickname)
        likes_dict[like.post_id].append(Like(id=like.id, post_id=like.post_id, user=user_info))
    return likes_dict

async def get_comments(post_ids: List[int], db: AsyncSession) -> dict:
    comment_query = select(Comments).where(Comments.post_id.in_(post_ids))
    comments_result = await db.execute(comment_query)
    comments = comments_result.scalars().all()
    comments_dict = defaultdict(list)
    for comment in comments:
        user_info = UserInfo(user_id=comment.user.user_id, avatar=comment.user.avatar, nickname=comment.user.nickname)
        comments_dict[comment.post_id].append(Comment(id=comment.id, post_id=comment.post_id, content=comment.content, created_at=comment.created_at, user=user_info, parent_id=comment.parent_id))
    return comments_dict
@router.post("/create_post", response_model=PostCreate)
async def create_post(post: PostCreate, db: AsyncSession = Depends(get_db)):
    pictures_data = [str(url) for url in post.pictures] if post.pictures else []
    query = insert(Post).values(
        user_id=post.user_id,
        content=post.content,
        pictures=pictures_data,  # 使用转换后的字符串列表
    )
    result = await db.execute(query)
    await db.commit()  # 确保提交事务以保存更改
    last_record_id = result.inserted_primary_key[0]
    return {**post.model_dump(), "id": last_record_id}
@router.post("/delete_post")
async def delete_post(user_id:int,post_id:int, db:AsyncSession=Depends(get_db)):
    query = Post.__table__.delete().where(Post.user_id == user_id,Post.id==post_id)
    await db.execute(query)
    await db.commit()
    return {"msg": "success"}

@router.post("/like_post")
async def like_post(like:PostLike, db:AsyncSession=Depends(get_db)):
    query = insert(Likes).values(
        post_id=like.post_id,
        user_id=like.user_id,
    )
    await db.execute(query)
    await db.commit()
    return {"msg": "success"}
@router.post("/comment_post")
async def comment_post(comment:PostComment, db=Depends(get_db)):
    query = insert(Comments).values(
        post_id=comment.post_id,
        user_id=comment.user_id,
        content=comment.content,
        parent_id=comment.parent_id
    )
    await db.execute(query)
    await db.commit()
    return {"msg": "success"}


@router.get("/get_friends_posts", response_model=List[OneMoment])
async def get_friends_posts(user_id: int, db: AsyncSession = Depends(get_db)):
    # 获取所有朋友的 ID
    query = select(Friends.from_id, Friends.to_id).where(
        or_(Friends.from_id == user_id, Friends.to_id == user_id)
    )
    result = await db.execute(query)
    rows = result.fetchall()
    # 提取朋友的 ID
    friend_ids = {row.from_id for row in rows if row.from_id != user_id}
    friend_ids.update(row.to_id for row in rows if row.to_id != user_id)
    moments = []
    # 获取所有朋友的帖子

    if friend_ids:
        query = (select(Post)
                 .options(selectinload(Post.likes), selectinload(Post.comments))
                 .where(Post.user_id.in_(friend_ids))
                 .order_by(Post.create_time.desc())
                 .limit(5))
        result = await db.execute(query)
        friend_posts = result.fetchall()
    else:
        friend_posts = []
    for friend_post in friend_posts:
        user=await get_user_by_id(friend_post.Post.user_id,db)
        moment=OneMoment(
            user=UserInfo(user_id=user.user_id,avatar=user.avatar,nickname=user.nickname),
            post=ReadPost(
                id=friend_post.Post.id,
                user_id=friend_post.Post.user_id,
                create_time=friend_post.Post.create_time,
                content=friend_post.Post.content,
                pictures=friend_post.Post.pictures,
                likes=[Like(id=like.id,post_id=like.post_id,user=UserInfo(user_id=like.user.user_id,avatar=like.user.avatar,nickname=like.user.nickname)) for like in friend_post.Post.likes],
                comments=[Comment(id=comment.id,post_id=comment.post_id,content=comment.content,created_at=comment.created_at,parent_id=comment.parent_id,user=UserInfo(user_id=comment.user.user_id,avatar=comment.user.avatar,nickname=comment.user.nickname)) for comment in friend_post.Post.comments]
            )
        )
        moments.append(moment)
    return moments

@router.get("/get_posts", response_model=List[PostModel])
async def get_my_posts(user_id: int, last_post_timestamp: Optional[datetime] = None, db: AsyncSession = Depends(get_db)):
    if not last_post_timestamp:
        last_post_timestamp = datetime.utcnow()
    query = select(Post).options(selectinload(Post.likes), selectinload(Post.comments)).where(
        Post.user_id == user_id,
        Post.create_time < last_post_timestamp
    ).order_by(Post.create_time.desc()).limit(5)
    my_posts=[]
    result = await db.execute(query)
    posts = result.scalars().all()
    for post in posts:
        my_post=PostModel(
            id=post.id,
            user_id=post.user_id,
            create_time=post.create_time,
            content=post.content,
            pictures=post.pictures,
            likes=[LikeModel(id=like.id,post_id=like.post_id,user_id=like.user_id) for like in post.likes],
            comments=[CommentModel(id=comment.id,post_id=comment.post_id,user_id=comment.user_id,content=comment.content,created_at=comment.created_at,parent_id=comment.parent_id) for comment in post.comments]
        )
        my_posts.append(my_post)
    return my_posts
