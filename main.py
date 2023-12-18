from fastapi import FastAPI
import uvicorn
from app.endpoint import moment
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("uvicorn.error")
app = FastAPI()

# 注册路由
app.include_router(moment.router)

# 启动 Uvicorn 服务器
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")