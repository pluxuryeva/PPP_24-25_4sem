import os
import sys
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from app.api import auth, bruteforce
from app.db.session import engine
from app.models.models import Base
from app.core.config import settings

# Создание таблиц в базе данных
Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION)

# Добавление CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене нужно указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(auth.router, tags=["auth"])
app.include_router(bruteforce.router, tags=["bruteforce"])


@app.get("/")
def read_root():
    return {"message": "Добро пожаловать в API брутфорса!"}


if __name__ == "__main__":
    # Запускаем приложение с текущего модуля
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 