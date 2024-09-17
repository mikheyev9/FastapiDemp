from datetime import datetime

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

note_tag_association = Table(
    'note_tag', Base.metadata,
    Column('note_id', ForeignKey('notes.id'), primary_key=True),
    Column('tag_id', ForeignKey('tags.id'), primary_key=True)
)


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, unique=True, index=True, nullable=False)  # Изменили тип на String
    hashed_password = Column(String, nullable=False)
    notes = relationship("Note", back_populates="user")


class Note(Base):
    __tablename__ = 'notes'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    content = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Внешний ключ на пользователя
    user_id = Column(Integer, ForeignKey('users.id'))

    # Связь с моделью User
    user = relationship("User", back_populates="notes")

    # Связь с тегами через ассоциативную таблицу
    tags = relationship('Tag', secondary=note_tag_association, back_populates='notes')


class Tag(Base):
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)

    # Связь с заметками через ассоциативную таблицу
    notes = relationship('Note', secondary=note_tag_association, back_populates='tags')
