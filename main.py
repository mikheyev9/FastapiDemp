from fastapi import FastAPI
from app.api import auth, notes
from app.db.session import engine
from app.db import models
from fastapi.middleware.cors import CORSMiddleware

# Инициализация приложения
app = FastAPI()

# Установка CORS, если необходимо (например, для работы с фронтендом)
origins = [
    "http://localhost",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Применение миграций при старте (автоматически создает таблицы)
@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(models.Base.metadata.create_all)

# Роуты для авторизации и заметок
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(notes.router, prefix="/notes", tags=["notes"])