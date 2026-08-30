from fastapi import FastAPI
from routers import news, users, favorite
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="头条")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(news.router)
app.include_router(users.router)
app.include_router(favorite.router)

@app.get("/")
async def hello():
    return {"message":"API running"}