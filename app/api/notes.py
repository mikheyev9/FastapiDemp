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


@router.get("/notes/{note_id}", response_model=schemas.Note)
async def get_note_by_id(note_id: int,
                         db: AsyncSession = Depends(get_db),
                         current_user: models.User = Depends(get_current_user)):
    # Ищем заметку по ID и проверяем, что она принадлежит текущему пользователю
    result = await db.execute(select(models.Note).filter(models.Note.id == note_id,
                                                         models.Note.user_id == current_user.id).options(selectinload(models.Note.tags)))
    db_note = result.scalar()

    if not db_note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    return db_note

@router.put("/notes/{note_id}", response_model=schemas.Note)
async def update_note(note_id: int,
                      note_update: schemas.NoteUpdate,
                      db: AsyncSession = Depends(get_db),
                      current_user: models.User = Depends(get_current_user)):
    # Ищем заметку по ID
    result = await db.execute(select(models.Note).filter(models.Note.id == note_id,
                                                         models.Note.user_id == current_user.id).options(selectinload(models.Note.tags)))
    db_note = result.scalar()

    if not db_note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    # Обновляем поля, если они предоставлены
    if note_update.title is not None:
        db_note.title = note_update.title
    if note_update.content is not None:
        db_note.content = note_update.content

    # Коммитим изменения
    await db.commit()
    await db.refresh(db_note)

    return db_note

@router.post("/notes/{note_id}/add_tag", response_model=schemas.Note)
async def add_tag_to_note(note_id: int, tag_name: str,
                          db: AsyncSession = Depends(get_db),
                          current_user: models.User = Depends(get_current_user)):
    # Ищем заметку по ID и подгружаем теги
    result = await db.execute(select(models.Note).filter(
        models.Note.id == note_id,
        models.Note.user_id == current_user.id
    ).options(selectinload(models.Note.tags)))
    db_note = result.scalar()

    if not db_note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    # Поиск или создание тега
    tag_result = await db.execute(select(models.Tag).filter(models.Tag.name == tag_name))
    tag = tag_result.scalar()
    if tag:
        if tag not in db_note.tags:
            db_note.tags.append(tag)
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag already added to the note")
    else:
        new_tag = models.Tag(name=tag_name)
        db.add(new_tag)
        db_note.tags.append(new_tag)

    # Коммитим изменения
    await db.commit()
    await db.refresh(db_note)

    return db_note



@router.delete("/notes/{note_id}/remove_tag", response_model=schemas.Note)
async def remove_tag_from_note(note_id: int, tag_name: str,
                               db: AsyncSession = Depends(get_db),
                               current_user: models.User = Depends(get_current_user)):
    # Ищем заметку по ID и подгружаем теги
    result = await db.execute(select(models.Note).filter(
        models.Note.id == note_id,
        models.Note.user_id == current_user.id
    ).options(selectinload(models.Note.tags)))
    db_note = result.scalar()

    if not db_note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    # Поиск тега
    tag_result = await db.execute(select(models.Tag).filter(models.Tag.name == tag_name))
    tag = tag_result.scalar()
    if tag and tag in db_note.tags:
        db_note.tags.remove(tag)
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Tag not found on the note")

    # Коммитим изменения
    await db.commit()
    await db.refresh(db_note)

    return db_note
