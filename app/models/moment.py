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
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
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


class Likes(Base):
    __tablename__ = "likes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey("posts.id"))
    user_id = Column(
        Integer, ForeignKey("lb_chat.id"), nullable=False, default=0, index=True
    )
    user = relationship("User")


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
    nickname = Column(String(100), nullable=False)
