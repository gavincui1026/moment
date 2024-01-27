import io
import json
import zipfile

import boto3
from botocore.exceptions import ClientError
import os


def upload_file(client, file_name, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = os.path.basename(file_name)

    try:
        client.upload_file(file_name, bucket, object_name)
    except ClientError as e:
        print(e)
        return False
    return True


def download_file(client, bucket, object_name, file_name):
    """Download a file from an S3 bucket

    :param bucket: Bucket to download from
    :param object_name: S3 object name
    :param file_name: Local file to save to
    :return: True if file was downloaded, else False
    """

    try:
        client.download_file(bucket, object_name, file_name)
    except ClientError as e:
        print(e)
        return False
    return True


def set_bucket_public_read(s3_client, bucket_name):
    """设置存储桶的策略，以允许公共读取访问"""

    bucket_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
            }
        ],
    }

    try:
        s3_client.put_bucket_policy(
            Bucket=bucket_name, Policy=json.dumps(bucket_policy)
        )
        return True
    except ClientError as e:
        print(e)
        return False


def create_function(
    lambda_client,
    bucket_name,
    function_name,
    role_arn,
    runtime="python3.8",
    handler_name="lambda_function.lambda_handler",
):
    """
    创建一个 AWS Lambda 函数。

    :param lambda_client: 已初始化的 Lambda Boto3 客户端
    :param bucket_name: 存储 Lambda 函数代码的 S3 桶名称
    :param function_name: 创建的 Lambda 函数的名称
    :param role_arn: 执行 Lambda 函数的 IAM 角色的 ARN
    :param runtime: Lambda 函数的运行时环境，默认为 Python 3.8
    :param handler_name: Lambda 函数的处理程序名称
    """

    # 假设代码存储在名为 lambda_function.py 的文件中
    code_file_name = "test_upload.py"
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a") as zf:
        zf.write(code_file_name)

    # 上传代码到 S3
    # s3_client = boto3.client("s3")
    # s3_client.upload_file(code_file_name, bucket_name, code_file_name)

    # 创建 Lambda 函数
    response = lambda_client.create_function(
        FunctionName=function_name,
        Runtime=runtime,
    )

    return response


if __name__ == "__main__":
    # s3 = boto3.client(
    #     "s3",
    #     endpoint_url="https://ams1.vultrobjects.com",
    #     aws_access_key_id="184S0F7JDAMJYYY4IOPS",
    #     aws_secret_access_key="3Ka78fA3OOBq6cQbJ5QWrMMKAYBxu0suKefEgnZs",
    # )
    # upload_file(
    #     s3,
    #     "1.jpg",
    #     "moment",
    #     "1.jpg",
    # )
    s3 = boto3.client(
        "s3",
        endpoint_url="https://ams1.vultrobjects.com",
        aws_access_key_id="184S0F7JDAMJYYY4IOPS",
        aws_secret_access_key="3Ka78fA3OOBq6cQbJ5QWrMMKAYBxu0suKefEgnZs",
        region_name="eu-central-1",
    )
    response = s3.list_buckets()
    print(response)
    client = boto3.client(
        "lambda",
        endpoint_url="https://ams1.vultrobjects.com",
        aws_access_key_id="184S0F7JDAMJYYY4IOPS",
        aws_secret_access_key="3Ka78fA3OOBq6cQbJ5QWrMMKAYBxu0suKefEgnZs",
        region_name="eu-central-1",
    )
    response = client.get_account_settings()
    print(response)
    # response = client.create_function(
    #     FunctionName="VideoThumbnail",
    #     Runtime="python3.12",
    #     Role="arn:aws:iam::184S0F7JDAMJYYY4IOPS:role/lambda-role",
    #     Code={
    #         "ZipFile": b"bytes",
    #         # "S3Bucket": "string",
    #         # "S3Key": "string",
    #     },
    # )
    # print(response)
    # create_function(
    #     lambda_client,
    #     "moment",
    #     "test",
    #     "arn:aws:iam::184S0F7JDAMJYYY4IOPS:role/lambda-role",
    # )
