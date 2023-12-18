from sqlalchemy import Column, String, Integer, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
Base=declarative_base()
class Token(Base):
    __tablename__ = 'lb_chat_token'
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String(32), nullable=False, server_default='', comment='用户ID')
    token = Column(String(255), nullable=False, server_default='', comment='token')