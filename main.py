from urllib.request import Request
from app.db.get_db import get_db
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from app.endpoint import moment, follow
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
# @app.middleware("http")
# async def token_auth_middleware(request: Request, call_next):
#     # 允许 CORS 预检请求直接通过
#     # if request.method == "OPTIONS":
#     #     headers = {
#     #         "Access-Control-Allow-Origin": "*",
#     #         "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
#     #         "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization",
#     #     }
#     #     return Response(status_code=200, headers=headers)
#
#     # 对于其他请求，执行原有的逻辑
#     if request.url.path in ["/docs", "/openapi.json"]:
#         return await call_next(request)
#
#     uid = request.headers.get('uid')
#     token = request.headers.get('api_token')
#     headers = {
#         "Access-Control-Allow-Origin": "*",  # 根据实际情况可能需要更严格的设置
#         "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
#         "Access-Control-Allow-Headers": "Origin, Content-Type, Accept, Authorization",
#         "Access-Control-Allow-Credentials": "true",  # 如果您需要凭证
#     }
#
#     if not uid or not token:
#         return JSONResponse(status_code=400, content={"detail": "缺少必要的认证参数"},headers=headers)
#
#     # db = get_db()
#     # if not await TokenOperations.check_user_token(uid, token, db):
#     #     return JSONResponse(status_code=401, content={"detail": "TOKEN验证失败"},headers=headers)
#
#     return await call_next(request)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
