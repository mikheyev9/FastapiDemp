from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from jose import JWTError, jwt
from app.db.session import get_db
from app.db import models
from app.schemas import user as schemas
from app.core.security import verify_password, get_password_hash, create_access_token
from config import settings
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
router = APIRouter()


# Регистрация пользователя
@router.post("/register", response_model=schemas.User)
async def register(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.User).filter(models.User.telegram_id == user.telegram_id))
    existing_user = result.scalar()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Telegram ID already registered")

    hashed_password = get_password_hash(user.password)
    db_user = models.User(telegram_id=user.telegram_id, hashed_password=hashed_password)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return schemas.User.from_orm(db_user)


@router.post("/login", response_model=schemas.UserWithToken)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # Telegram ID берется из username
    telegram_id = form_data.username

    # Ищем пользователя по Telegram ID
    result = await db.execute(select(models.User).filter(models.User.telegram_id == telegram_id))
    db_user = result.scalar()

    # Проверка существования пользователя и пароля
    if not db_user or not verify_password(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect Telegram ID or password")

    # Генерация JWT токена
    access_token = create_access_token({"sub": db_user.telegram_id})

    # Возвращаем токен и данные пользователя
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": schemas.User.from_orm(db_user)
    }

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        print(f"Token received: {token}")
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        telegram_id: str = payload.get("sub")
        print('Token id', telegram_id)
        if telegram_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    result = await db.execute(select(models.User).filter(models.User.telegram_id == telegram_id))
    user = result.scalar()
    if user is None:
        raise credentials_exception
    return user
