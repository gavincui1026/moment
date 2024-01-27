from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    JSON,
    Text,
    SmallInteger,
    DECIMAL,
    select,
    desc,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    __tablename__ = "lb_chat"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String(32), nullable=False, default="", comment="用户ID")
    user_key = Column(String(32), nullable=False, default="", comment="登录验证KEY")
    nickname = Column(String(100), nullable=False, default="", comment="昵称")
    avatar = Column(String(500), nullable=False, default="", comment="头像")
    mobile = Column(String(50), nullable=False, default="", comment="手机号")
    create_time = Column(Integer, nullable=False, default=0, comment="创建时间")
    update_time = Column(Integer, nullable=False, default=0, comment="更新时间")
    sex = Column(SmallInteger, nullable=False, default=0, comment="性别0/1/2")
    province = Column(String(50), nullable=False, default="", comment="省份")
    city = Column(String(50), nullable=False, default="", comment="城市")
    intro = Column(String(256), nullable=False, default="", comment="介绍或签名")
    mid = Column(String(32), nullable=False, default="", comment="外部ID")
    pinyin = Column(String(1), nullable=False, default="", comment="首字母")
    is_edit = Column(SmallInteger, nullable=False, default=0, comment="可编辑")
    custom = Column(Text, comment="自定义扩展内容")


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(
        Integer, ForeignKey("lb_chat.id"), nullable=False, default=0, index=True
    )
    create_time = Column(DateTime, default=func.now())
    content = Column(Text)
    pictures = Column(JSON)
    likes = relationship("Likes", backref="post")
    comments = relationship("Comments", backref="post")
    user = relationship("User")

    @classmethod
    async def get_posts(cls, user_list: list, page, page_size, db):
        query = (
            select(cls)
            .where(cls.user_id.in_(user_list))
            .options(
                selectinload(cls.likes).selectinload(Likes.user),
                selectinload(cls.comments).selectinload(Comments.user),
                selectinload(cls.user),
            )
            .order_by(desc(cls.create_time))
            .offset(page * page_size)  # 跳过前面的页数
            .limit(page_size)  # 返回当前页的条目
        )
        result = await db.execute(query)
        posts = result.scalars().all()
        total = select(func.count(cls.id)).where(cls.user_id.in_(user_list))
        result = await db.execute(total)
        total = result.scalar()
        return posts, total

    @classmethod
    async def get_userid(cls, post_id: int, db):
        query = select(cls).where(cls.id == post_id)
        result = await db.execute(query)
        post = result.scalars().first()
        return post.user_id

    @classmethod
    async def get_post(cls, post_id: int, db):
        query = select(cls).where(cls.id == post_id)
        result = await db.execute(query)
        post = result.scalars().first()
        return post


class Likes(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(
        Integer, ForeignKey("lb_chat.id"), nullable=False, default=0, index=True
    )
    user = relationship("User")

    @classmethod
    async def is_liked(cls, user_id: int, post_id: int, db):
        query = select(cls).where(cls.user_id == user_id, cls.post_id == post_id)
        result = await db.execute(query)
        like = result.scalars().first()
        if like:
            return True
        else:
            return False


class Comments(Base):
    __tablename__ = "comments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(
        Integer, ForeignKey("lb_chat.id"), nullable=False, default=0, index=True
    )
    content = Column(Text)
    created_at = Column(DateTime, default=func.now())
    parent_id = Column(Integer, default=0)
    user = relationship("User")


class Friends(Base):
    __tablename__ = "lb_chat_friend"
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    from_id = Column(Integer, nullable=False, default=0, index=True)
    to_id = Column(Integer, nullable=False, default=0, index=True)
    nickname = Column(String(100), nullable=False, default="")
    status = Column(SmallInteger, nullable=False, default=1)
    is_block = Column(SmallInteger, nullable=False, default=0)

    @classmethod
    async def get_all_friends(cls, user_id: int, db):
        query = select(cls).where(cls.from_id == user_id)
        result = await db.execute(query)
        friends = result.scalars().all()
        friends_list = []
        for friend in friends:
            query = select(User).where(User.id == friend.to_id)
            result = await db.execute(query)
            user = result.scalars().first()
            friends_list.append(user)
        return friends_list


class Block(Base):
    __tablename__ = "lb_user_block"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, default=0, index=True)
    to_user_id = Column(Integer, nullable=False, default=0, index=True)
    create_time = Column(Integer, nullable=False, default=0)

    @classmethod
    async def is_block(cls, user_id: int, to_user_id: int, db2):
        query = select(cls).where(cls.user_id == user_id, cls.to_user_id == to_user_id)
        result = await db2.execute(query)
        block = result.scalars().first()
        if block:
            return True
        else:
            return False


class AddonUser(Base):
    __tablename__ = "lb_user"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="ID")
    mid = Column(String(20), nullable=True, default="", comment="外部ID")
    password = Column(String(128), nullable=False, default="", comment="密码")
    user_name = Column(String(80), nullable=False, default="", comment="用户名")
    user_nickname = Column(String(80), nullable=False, default="", comment="昵称")
    mobile = Column(String(50), nullable=False, default="", comment="手机号")
    head_img = Column(String(256), nullable=False, default="", comment="头像")
    user_email = Column(String(100), nullable=False, default="", comment="用户邮箱")
    last_login_time = Column(Integer, nullable=False, default=0, comment="最后登录时间")
    last_login_ip = Column(Integer, nullable=False, default=0, comment="最后登录ip")
    create_time = Column(Integer, nullable=False, default=0, comment="创建时间")
    update_time = Column(Integer, nullable=False, default=0, comment="更新时间")
    status = Column(SmallInteger, nullable=False, default=1, comment="状态")
    lastid = Column(Integer, nullable=False, default=0, comment="邀请人")
    last_time = Column(Integer, nullable=False, default=0, comment="邀请我的时间")
    score = Column(DECIMAL(20, 2), nullable=False, default=0.00, comment="积分")
    user_money = Column(DECIMAL(20, 2), nullable=False, default=0.00, comment="余额")
    total_consumption_money = Column(
        DECIMAL(20, 2), nullable=False, default=0.00, comment="总计消费"
    )
    freeze_money = Column(DECIMAL(20, 0), nullable=False, default=0, comment="冻结金额")
    chat_uid = Column(
        String(32), nullable=False, default="", comment="注册到聊天模块的ID"
    )
    chat_user_key = Column(
        String(32), nullable=False, default="", comment="注册到聊天模块的key"
    )
    pay_password = Column(String(64), nullable=False, default="", comment="支付密码")
    is_delete = Column(SmallInteger, nullable=False, default=0, comment="是否已注销")
    user_level = Column(Integer, nullable=False, default=0, comment="等级")
