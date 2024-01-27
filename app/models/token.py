from sqlalchemy import Column, String, Integer, DateTime, func, null, SmallInteger
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class Token(Base):
    __tablename__ = "lb_chat_token"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(String(32), nullable=False, server_default="", comment="用户ID")
    token = Column(String(255), nullable=False, server_default="", comment="token")


class AddonToken(Base):
    __tablename__ = "lb_admin_api_app_token"
    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, nullable=False, comment="用户ID")
    apptoken = Column(String(50), nullable=False, comment="应用appToken")


class Upload(Base):
    __tablename__ = "lb_upload"

    id = Column(Integer, primary_key=True, autoincrement=True)
    uid = Column(Integer, default=0, comment="用户id")
    name = Column(String(255), default="", comment="文件名")
    module = Column(String(32), default="", comment="模块名")
    path = Column(String(255), default="", comment="文件路径")
    thumb = Column(String(255), default="", comment="缩略图路径")
    url = Column(String(255), default="", comment="文件链接")
    mime = Column(String(128), default="", comment="文件mime类型")
    ext = Column(String(8), default="", comment="文件类型")
    size = Column(Integer, default=0, comment="文件大小")
    md5 = Column(String(32), default="", comment="文件md5")
    sha1 = Column(String(40), default="", comment="sha1 散列值")
    driver = Column(String(16), default="local", comment="上传驱动")
    download = Column(Integer, default=0, comment="下载次数")
    create_time = Column(Integer, default=0, comment="上传时间")
    update_time = Column(Integer, default=0, comment="更新时间")
    sort = Column(Integer, default=100, comment="排序")
    status = Column(SmallInteger, default=1, comment="状态")
    width = Column(Integer, default=0, comment="图片宽度")
    height = Column(Integer, default=0, comment="图片高度")
    duration = Column(Integer, default=0, comment="时长")
    key = Column(String(255), default="", comment="文件KEY")
