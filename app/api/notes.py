from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import selectinload

from app.db import models
from app.schemas import note as schemas
from app.db.session import get_db
from app.api.auth import get_current_user  # Импортируем get_current_user
from typing import List

router = APIRouter()


@router.get("/notes/", response_model=List[schemas.Note])
async def get_notes(tag: str = None,
                    db: AsyncSession = Depends(get_db),
                    current_user: models.User = Depends(get_current_user)):
    query = select(models.Note).where(models.Note.user_id == current_user.id).options(selectinload(models.Note.tags))

    if tag:
        query = query.filter(models.Note.tags.any(models.Tag.name == tag))

    result = await db.execute(query)
    return result.scalars().all()


@router.post("/notes/", response_model=schemas.Note)
async def create_note(note: schemas.NoteCreate,
                      db: AsyncSession = Depends(get_db),
                      current_user: models.User = Depends(get_current_user)):
    db_note = models.Note(title=note.title, content=note.content, user_id=current_user.id)

    for tag_name in note.tags:
        tag_result = await db.execute(select(models.Tag).filter(models.Tag.name == tag_name))
        tag = tag_result.scalar()
        if tag:
            db_note.tags.append(tag)
        else:
            new_tag = models.Tag(name=tag_name)
            db.add(new_tag)
            db_note.tags.append(new_tag)

    db.add(db_note)
    await db.commit()
    await db.refresh(db_note)

    # Ручная подгрузка тегов после коммита
    await db.execute(select(models.Note).options(selectinload(models.Note.tags)).filter(models.Note.id == db_note.id))

    return db_note

