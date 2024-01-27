from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.token import Upload
from app.schemas.callback import CallbackModel
from app.schemas.get_sign import Get_SignModel
import re
import os
from typing import Optional, List


# 秒传验证，如果md5存在则返回文件信息
async def get_callback(filemd5: str, db: AsyncSession) -> CallbackModel | None:
    query = select(Upload).where(Upload.md5 == filemd5)
    callback = await db.execute(query)
    callback = callback.scalars().first()
    if callback:
        return CallbackModel(
            id=callback.id,
            name=callback.name,
            path=callback.path,
            md5=callback.md5,
            duration=callback.duration,
        )
    # result = await db.execute(query)
    # callback = result.scalars().first()
    # return CallbackModel(
    #     id=callback.id,
    #     name=callback.name,
    #     path=callback.path,
    #     md5=callback.md5,
    #     duration=callback.duration,
    # )


# 直传，首先验证文件的各种信息是否正确，然后进行上传，并返回文件信息


async def validator(get_sign: Get_SignModel):
    md5 = get_sign.md5
    if not re.match(r"^[a-fA-F0-9]{32}$", md5):
        raise Exception("filemd5参数不正确")
    upload_file_ext = ["txt", "pdf", "mp4"]
    upload_image_ext = ["jpg", "png"]
    # 获取MIME类型前缀
    type = get_sign.mime.split("/")[0]

    # 获取文件扩展名并转换为小写
    ext = os.path.splitext(get_sign.name)[1].lower().lstrip(".")
    # 检查文件类型和扩展名
    if type == "image" and ext not in upload_image_ext:
        raise Exception("上传的文件不在允许上传列中")

    if type != "image" and ext not in upload_file_ext:
        raise Exception("上传的文件不在允许上传列中")

    # 检查音视频文件的时长
    if type in ["audio", "video"] and get_sign.duration <= 0:
        raise Exception("上传的是音视频文件，时长参数(duration)必传")

    # 检查文件大小（假设限制为1GB）
    max_size = 1024 * 1024 * 1024  # 1GB
    if get_sign.size > max_size:
        raise Exception("文件尺寸过大，请上传不超过1G的文件")


import boto3
from botocore.exceptions import NoCredentialsError


def create_presigned_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    # Create a S3 client
    s3_client = boto3.client("s3")

    try:
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration,
        )
    except NoCredentialsError as e:
        print(e)
        return None

    return response


async def read_path_by_id(ids: List, db: AsyncSession) -> Optional[str]:
    pass
