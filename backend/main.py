from contextlib import asynccontextmanager
from fastapi import FastAPI
from routers.chat import router as chat_router
from db.database import engine
from db.models import Base

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(chat_router, tags=["chat"])