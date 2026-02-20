from __future__ import annotations

from sqlalchemy import String, Integer, Text, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Word(Base):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    headword: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    phonetic: Mapped[str | None] = mapped_column(String(64), nullable=True)
    pos: Mapped[str | None] = mapped_column(String(32), nullable=True)
    meaning_zh: Mapped[str] = mapped_column(String(255))
    meaning_en: Mapped[str | None] = mapped_column(String(255), nullable=True)
    example_en: Mapped[str | None] = mapped_column(Text, nullable=True)
    example_zh: Mapped[str | None] = mapped_column(Text, nullable=True)
    etymology: Mapped[str | None] = mapped_column(Text, nullable=True)

    options: Mapped[list[WordOption]] = relationship(
        "WordOption", back_populates="word", cascade="all, delete-orphan"
    )


class WordOption(Base):
    __tablename__ = "word_options"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"), index=True)
    option_text_zh: Mapped[str] = mapped_column(String(255))
    is_correct: Mapped[int] = mapped_column(Integer, default=0)  # 0/1

    word: Mapped[Word] = relationship("Word", back_populates="options")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    nickname: Mapped[str] = mapped_column(String(64), default="游客")


class UserPlan(Base):
    __tablename__ = "user_plans"
    __table_args__ = (UniqueConstraint("user_id", name="uniq_user_plan"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    daily_new: Mapped[int] = mapped_column(Integer, default=20)


class UserWordProgress(Base):
    __tablename__ = "user_word_progress"
    __table_args__ = (UniqueConstraint("user_id", "word_id", name="uniq_user_word"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"), index=True)

    status: Mapped[str] = mapped_column(String(16), default="new")  # new/learning/mastered
    seen_count: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    date_yyyymmdd: Mapped[str] = mapped_column(String(8), index=True)


class LearningSessionItem(Base):
    __tablename__ = "learning_session_items"
    __table_args__ = (UniqueConstraint("session_id", "word_id", name="uniq_session_word"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("learning_sessions.id"), index=True)
    word_id: Mapped[int] = mapped_column(ForeignKey("words.id"), index=True)

    answered: Mapped[int] = mapped_column(Integer, default=0)
    is_correct: Mapped[int | None] = mapped_column(Integer, nullable=True)
