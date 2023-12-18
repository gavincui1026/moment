from typing import Optional

from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, JSON,Text
from sqlalchemy.ext.declarative import declarative_base
# 定义朋友圈帖子模型
Base = declarative_base()
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()

class User(Base):
    __tablename__ = 'lb_chat'
    user_id = Column(Integer, nullable=False, default=0, index=True,name='id',primary_key=True)
    avatar = Column(String(255))
    nickname = Column(String(50))

class Post(Base):
    __tablename__ = 'posts'
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('lb_chat.id'), nullable=False, default=0, index=True)
    create_time = Column(DateTime, default=func.now())
    content = Column(Text)
    pictures = Column(JSON)
    likes = relationship('Likes', backref='post')
    comments = relationship('Comments', backref='post')

class Likes(Base):
    __tablename__ = 'likes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    user_id = Column(Integer, ForeignKey('lb_chat.id'), nullable=False, default=0, index=True)
    relationship('User', backref='likes')


class Comments(Base):
    __tablename__ = 'comments'
    id = Column(Integer, primary_key=True, autoincrement=True)
    post_id = Column(Integer, ForeignKey('posts.id'))
    user_id = Column(Integer, ForeignKey('lb_chat.id'), nullable=False, default=0, index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=func.now())
class Friends(Base):
    __tablename__ = 'lb_chat_friend'
    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    from_id = Column(Integer, nullable=False, default=0, index=True)
    to_id = Column(Integer, nullable=False, default=0, index=True)
    nickname = Column(String(100), nullable=False)

