import logging
from fastapi import FastAPI

from app.config import Settings
from app.routers import items

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

settings = Settings()

app = FastAPI(
    title=settings.app_name,
    description="Лабораторная работа по FastAPI",
    version="1.0.0",
    contact={
        "name": "Студент",
        "email": settings.admin_email,
    },
)

app.include_router(items.router)


@app.get("/")
def read_root():
    logger.info("Запрос к корневому эндпоинту /")
    return {"message": "Hello, FastAPI!"}


@app.get("/info")
def get_info():
    logger.info("Запрос информации о настройках /info")
    return {
        "app_name": settings.app_name,
        "admin_email": settings.admin_email,
        "items_per_page": settings.items_per_page,
    }