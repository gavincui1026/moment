from http.client import HTTPException
from urllib.request import Request
from app.db.get_db import get_db
from fastapi import FastAPI
import uvicorn
from app.endpoint import moment
import logging
from app.auth.verify_token import TokenOperations
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("uvicorn.error")
app = FastAPI()

# 注册路由
app.include_router(moment.router)
@app.middleware("http")
async def token_auth_middleware(request: Request, call_next):
    if request.url.path in ["/docs", "/openapi.json"]:
        return await call_next(request)
    uid = request.headers.get('uid')
    token = request.headers.get('api_token')

    if not uid or not token:
        return HTTPException(status_code=400, detail="缺少必要的认证参数")
    async with get_db() as db:
        if not await TokenOperations.check_user_token(uid, token, db):
            return HTTPException(status_code=401, detail="TOKEN验证失败")

    # 如果验证通过，继续处理请求
    response = await call_next(request)
    return response
# 启动 Uvicorn 服务器
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")