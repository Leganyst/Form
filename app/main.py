# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.database import engine, Base
from app.models import combined, user, lead, collector, notification, user_notification_status
from app.routers.api.user import router as user_router
from app.routers.api.auth import router as auth_router



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
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
app.include_router(user_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
