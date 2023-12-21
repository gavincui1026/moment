# 使用官方 Python 基础镜像
FROM python:3.11.4

# 设置工作目录
WORKDIR /moment

# 复制项目文件到容器中
COPY . /moment

# 安装依赖
RUN pip install -r requirements.txt
run pip install gunicorn
# 指定对外暴露的端口
EXPOSE 8000

# 定义启动命令
CMD ["gunicorn", "-w 4", "b", "app:app", "--reload"]