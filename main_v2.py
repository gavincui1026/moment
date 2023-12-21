

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


@app.get("/")
async def index():
    return {"message": "OK"}


@app.post("/")
async def send():
    return {"message": "Hello"}

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)




if __name__ == "__main__":
    uvicorn.run("main_v2:app", host="127.0.0.1", reload=True)
