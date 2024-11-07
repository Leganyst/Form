# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import engine, Base
from app.models import user, lead, collector, notification, user_notification_status



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()


# @app.on_event("startup")
# async def startup():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)

# @app.on_event("shutdown")
# async def shutdown():
#     await engine.dispose()

app = FastAPI(lifespan=lifespan)
# app.include_router(user.router, prefix="/api")
