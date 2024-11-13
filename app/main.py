# app/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html
from app.core.database import engine, Base
from app.models import combined, user, lead, collector, notification, user_notification_status
from app.routers.api.user import router as user_router
from app.routers.api.auth import router as auth_router
from app.routers.api.collector import router as collector_router
from app.routers.api.notification import router as notification_router



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

app = FastAPI(lifespan=lifespan, swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})

origins = [
    "https://*.vercel.app",
    "https://*.wormhole.vk-apps.com",
    "https://*.pages.vk-apps.com",
    "https://*.pages-ac.vk-apps.com",
    "https://pages-ac.vk-apps.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "HEAD", "PATCH"],
    allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
)

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        swagger_css_url="https://cdn.jsdelivr.net/gh/Itz-fork/Fastapi-Swagger-UI-Dark/assets/swagger_ui_dark.min.css"
    )

app.include_router(user_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(collector_router, prefix="/api")
app.include_router(notification_router, prefix="/api")