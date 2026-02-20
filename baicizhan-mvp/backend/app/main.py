from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from .settings import settings
from .db import Base, engine, get_db
from .models import (
    Word,
    WordOption,
    User,
    UserPlan,
    UserWordProgress,
    LearningSession,
    LearningSessionItem,
)


DEMO_USER_ID = 1


class PlanOut(BaseModel):
    daily_new: int
    total_words: int
    learned_words: int
    remaining_days: int


class OptionOut(BaseModel):
    id: int
    text: str


class WordQuizOut(BaseModel):
    session_id: int
    word_id: int
    headword: str
    phonetic: str | None
    pos: str | None
    options: list[OptionOut]


class AnswerIn(BaseModel):
    option_id: int


class AnswerOut(BaseModel):
    correct: bool
    correct_option_id: int
    meaning_zh: str
    example_en: str | None
    example_zh: str | None
    etymology: str | None


class WordDetailOut(BaseModel):
    word_id: int
    headword: str
    phonetic: str | None
    pos: str | None
    meaning_zh: str
    meaning_en: str | None
    example_en: str | None
    example_zh: str | None
    etymology: str | None
    similar_words: list[str]


def today_yyyymmdd() -> str:
    return datetime.utcnow().strftime("%Y%m%d")


def ensure_seed(db: Session):
    seed_flag = os.getenv("SEED_ON_STARTUP", "true").lower() in ("1", "true", "yes")
    if not seed_flag:
        return

    # ensure demo user
    user = db.get(User, DEMO_USER_ID)
    if not user:
        user = User(id=DEMO_USER_ID, nickname="Yorick")
        db.add(user)
        db.flush()

    plan = db.execute(select(UserPlan).where(UserPlan.user_id == DEMO_USER_ID)).scalar_one_or_none()
    if not plan:
        db.add(UserPlan(user_id=DEMO_USER_ID, daily_new=20))

    # seed words only when empty
    words_count = db.execute(select(func.count()).select_from(Word)).scalar_one()
    if words_count and words_count > 0:
        db.commit()
        return

    seed_path = Path(__file__).resolve().parent.parent / "data" / "seed_words.json"
    data: list[dict[str, Any]] = json.loads(seed_path.read_text(encoding="utf-8"))

    for w in data:
        word = Word(
            headword=w["headword"],
            phonetic=w.get("phonetic"),
            pos=w.get("pos"),
            meaning_zh=w["meaning_zh"],
            meaning_en=w.get("meaning_en"),
            example_en=w.get("example_en"),
            example_zh=w.get("example_zh"),
            etymology=w.get("etymology"),
        )
        db.add(word)
        db.flush()
        for opt in w["options"]:
            db.add(
                WordOption(
                    word_id=word.id,
                    option_text_zh=opt["text"],
                    is_correct=1 if opt.get("correct") else 0,
                )
            )

    db.commit()


def get_or_create_session(db: Session, user_id: int, date_yyyymmdd: str) -> LearningSession:
    session = db.execute(
        select(LearningSession).where(
            LearningSession.user_id == user_id,
            LearningSession.date_yyyymmdd == date_yyyymmdd,
        )
    ).scalar_one_or_none()
    if session:
        return session

    session = LearningSession(user_id=user_id, date_yyyymmdd=date_yyyymmdd)
    db.add(session)
    db.flush()

    plan = db.execute(select(UserPlan).where(UserPlan.user_id == user_id)).scalar_one()

    # pick new words not yet in progress
    subq = select(UserWordProgress.word_id).where(UserWordProgress.user_id == user_id)
    candidates = db.execute(select(Word).where(Word.id.not_in(subq)).limit(plan.daily_new)).scalars().all()

    # fallback: if not enough new words, just take remaining
    if len(candidates) < plan.daily_new:
        more = db.execute(select(Word).limit(plan.daily_new)).scalars().all()
        seen = {c.id for c in candidates}
        for m in more:
            if m.id not in seen:
                candidates.append(m)
            if len(candidates) >= plan.daily_new:
                break

    for w in candidates:
        db.add(LearningSessionItem(session_id=session.id, word_id=w.id, answered=0))
        # ensure progress row exists
        prog = db.execute(
            select(UserWordProgress).where(UserWordProgress.user_id == user_id, UserWordProgress.word_id == w.id)
        ).scalar_one_or_none()
        if not prog:
            db.add(UserWordProgress(user_id=user_id, word_id=w.id, status="learning"))

    db.commit()
    db.refresh(session)
    return session


app = FastAPI(title="Baicizhan Web MVP API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    # MVP：为便于本地调试与AnyGen预览环境，直接放开跨域。
    # 生产环境请改为白名单（例如 http://localhost:5173）。
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)
    from .db import SessionLocal

    db = SessionLocal()
    try:
        ensure_seed(db)
    finally:
        db.close()


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/api/plan", response_model=PlanOut)
def get_plan(db: Session = Depends(get_db)):
    plan = db.execute(select(UserPlan).where(UserPlan.user_id == DEMO_USER_ID)).scalar_one()
    total = db.execute(select(func.count()).select_from(Word)).scalar_one()
    learned = db.execute(
        select(func.count()).select_from(UserWordProgress).where(
            UserWordProgress.user_id == DEMO_USER_ID,
            UserWordProgress.status.in_(["learning", "mastered"]),
        )
    ).scalar_one()

    remaining = max(total - learned, 0)
    remaining_days = max((remaining + plan.daily_new - 1) // plan.daily_new, 0)
    return PlanOut(daily_new=plan.daily_new, total_words=total, learned_words=learned, remaining_days=remaining_days)


@app.post("/api/session/start", response_model=dict)
def start_session(db: Session = Depends(get_db)):
    s = get_or_create_session(db, DEMO_USER_ID, today_yyyymmdd())
    return {"session_id": s.id}


@app.get("/api/session/{session_id}/next", response_model=WordQuizOut)
def next_word(session_id: int, db: Session = Depends(get_db)):
    item = (
        db.execute(
            select(LearningSessionItem)
            .where(
                LearningSessionItem.session_id == session_id,
                LearningSessionItem.answered == 0,
            )
            .order_by(LearningSessionItem.id.asc())
        )
        .scalars()
        .first()
    )

    if not item:
        raise HTTPException(status_code=404, detail="no_more_words")

    word = db.get(Word, item.word_id)
    opts = db.execute(select(WordOption).where(WordOption.word_id == word.id)).scalars().all()

    return WordQuizOut(
        session_id=session_id,
        word_id=word.id,
        headword=word.headword,
        phonetic=word.phonetic,
        pos=word.pos,
        options=[OptionOut(id=o.id, text=o.option_text_zh) for o in opts],
    )


@app.post("/api/session/{session_id}/word/{word_id}/answer", response_model=AnswerOut)
def answer(session_id: int, word_id: int, payload: AnswerIn, db: Session = Depends(get_db)):
    item = db.execute(
        select(LearningSessionItem).where(
            LearningSessionItem.session_id == session_id,
            LearningSessionItem.word_id == word_id,
        )
    ).scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="session_word_not_found")

    if item.answered == 1:
        raise HTTPException(status_code=400, detail="already_answered")

    chosen = db.get(WordOption, payload.option_id)
    if not chosen or chosen.word_id != word_id:
        raise HTTPException(status_code=400, detail="invalid_option")

    correct_opt = db.execute(
        select(WordOption).where(WordOption.word_id == word_id, WordOption.is_correct == 1)
    ).scalar_one()

    correct = chosen.id == correct_opt.id

    item.answered = 1
    item.is_correct = 1 if correct else 0

    prog = db.execute(
        select(UserWordProgress).where(UserWordProgress.user_id == DEMO_USER_ID, UserWordProgress.word_id == word_id)
    ).scalar_one()
    prog.seen_count += 1
    if correct:
        prog.correct_count += 1

    if prog.correct_count >= 2:
        prog.status = "mastered"

    db.commit()

    word = db.get(Word, word_id)
    return AnswerOut(
        correct=correct,
        correct_option_id=correct_opt.id,
        meaning_zh=word.meaning_zh,
        example_en=word.example_en,
        example_zh=word.example_zh,
        etymology=word.etymology,
    )


@app.get("/api/words/{word_id}", response_model=WordDetailOut)
def word_detail(word_id: int, db: Session = Depends(get_db)):
    word = db.get(Word, word_id)
    if not word:
        raise HTTPException(status_code=404, detail="word_not_found")

    # naive similar words: same suffix/prefix length heuristic
    prefix = word.headword[:3]
    similar = db.execute(
        select(Word.headword).where(Word.headword.like(f"{prefix}%"), Word.id != word_id).limit(6)
    ).scalars().all()

    return WordDetailOut(
        word_id=word.id,
        headword=word.headword,
        phonetic=word.phonetic,
        pos=word.pos,
        meaning_zh=word.meaning_zh,
        meaning_en=word.meaning_en,
        example_en=word.example_en,
        example_zh=word.example_zh,
        etymology=word.etymology,
        similar_words=similar,
    )
