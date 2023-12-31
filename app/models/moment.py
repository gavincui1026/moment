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
    nickname = Column(String(100), nullable=False, default="")
    status = Column(SmallInteger, nullable=False, default=1)
    is_block = Column(SmallInteger, nullable=False, default=0)


class Block(Base):
    __tablename__ = "lb_user_block"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False, default=0, index=True)
    to_user_id = Column(Integer, nullable=False, default=0, index=True)
    create_time = Column(Integer, nullable=False, default=0)


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
