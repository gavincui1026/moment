from urllib.request import Request
from app.db.get_db import get_db
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import uvicorn
from app.endpoint import moment, follow, get_oss_sign, rest
from app.push.fcm_push import FirebasePush
from starlette.responses import Response
import logging
from fastapi.middleware.cors import CORSMiddleware


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("uvicorn.error")
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有源
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头
)
# 注册路由
app.include_router(moment.router, prefix="/api")
app.include_router(follow.router, prefix="/api")
app.include_router(get_oss_sign.route, prefix="/api")
app.include_router(rest.router, prefix="/api")


@app.on_event("startup")
async def push():
    push = FirebasePush()
    background_tasks = BackgroundTasks()
    background_tasks.add_task(push.start)
    await background_tasks()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="debug",
        reload=True,
    )
