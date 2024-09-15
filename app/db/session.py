from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from config import settings

# Создаем базовый класс для наших моделей
Base = declarative_base()

# Создаем асинхронный движок для работы с базой данных
engine = create_async_engine(settings.DATABASE_URL, future=True, echo=True)

# Создаем асинхронную сессию для взаимодействия с базой данных
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

# Создаем функцию для получения сессии
async def get_db():
    async with SessionLocal() as session:
        yield session