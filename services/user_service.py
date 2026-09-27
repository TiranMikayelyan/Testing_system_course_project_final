"""User registration, authentication, and settings."""

from __future__ import annotations

import re

import bcrypt
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from config import (
    DEFAULT_DURATION_MINUTES,
    DEFAULT_LANGUAGE,
    DEFAULT_QUESTIONS,
    DEFAULT_SOUND,
    DEFAULT_THEME,
)
from database.repositories.settings_repo import UserSettingsRecord
from database.repositories.test_result_repo import TestResultRecord
from database.repositories.user_repo import UserRecord
from models.user import User


class UserServiceError(Exception):
    pass


class UserService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def register(self, username: str, password: str, display_name: str) -> User:
        username = username.strip()
        display_name = display_name.strip() or username

        if not self._valid_username(username):
            raise UserServiceError(
                "Username must be 3–32 characters (letters, numbers, underscore)."
            )
        if len(password) < 6:
            raise UserServiceError("Password must be at least 6 characters.")

        existing = self.db.scalar(
            select(UserRecord).where(UserRecord.username == username)
        )
        if existing:
            raise UserServiceError("Username already exists.")

        password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

        record = UserRecord(
            username=username,
            password_hash=password_hash,
            display_name=display_name,
        )
        self.db.add(record)
        self.db.flush()

        settings = UserSettingsRecord(user_id=record.id)
        self.db.add(settings)
        self.db.commit()
        self.db.refresh(record)

        return User(id=record.id, username=record.username, display_name=record.display_name)

    def login(self, username: str, password: str) -> User:
        record = self.db.scalar(
            select(UserRecord).where(UserRecord.username == username.strip())
        )
        if not record:
            raise UserServiceError("Invalid username or password.")

        if not bcrypt.checkpw(
            password.encode("utf-8"), record.password_hash.encode("utf-8")
        ):
            raise UserServiceError("Invalid username or password.")

        return User(
            id=record.id,
            username=record.username,
            display_name=record.display_name,
        )

    def get_settings(self, user_id: int) -> dict:
        record = self.db.scalar(
            select(UserSettingsRecord).where(UserSettingsRecord.user_id == user_id)
        )
        if not record:
            return self._default_settings()
        return {
            "theme": record.theme or DEFAULT_THEME,
            "sound_enabled": record.sound_enabled == "true",
            "language": record.language or DEFAULT_LANGUAGE,
            "default_questions": record.default_questions or DEFAULT_QUESTIONS,
            "default_duration": record.default_duration or DEFAULT_DURATION_MINUTES,
        }

    def save_settings(self, user_id: int, settings: dict) -> None:
        record = self.db.scalar(
            select(UserSettingsRecord).where(UserSettingsRecord.user_id == user_id)
        )
        if not record:
            record = UserSettingsRecord(user_id=user_id)
            self.db.add(record)

        record.theme = settings.get("theme", DEFAULT_THEME)
        record.sound_enabled = "true" if settings.get("sound_enabled", True) else "false"
        record.language = settings.get("language", DEFAULT_LANGUAGE)
        record.default_questions = int(
            settings.get("default_questions", DEFAULT_QUESTIONS)
        )
        record.default_duration = int(
            settings.get("default_duration", DEFAULT_DURATION_MINUTES)
        )
        self.db.commit()

    def get_statistics(self, user_id: int) -> dict:
        results = self.db.scalars(
            select(TestResultRecord)
            .where(TestResultRecord.user_id == user_id)
            .order_by(TestResultRecord.completed_at.desc())
        ).all()

        if not results:
            return {
                "tests_completed": 0,
                "average_score": 0.0,
                "best_score": 0.0,
                "recent": [],
            }

        percentages = [r.percentage for r in results]
        recent = [
            {"topic": r.topic, "percentage": r.percentage, "date": r.completed_at}
            for r in results[:5]
        ]
        return {
            "tests_completed": len(results),
            "average_score": round(sum(percentages) / len(percentages), 1),
            "best_score": round(max(percentages), 1),
            "recent": recent,
        }

    @staticmethod
    def _valid_username(username: str) -> bool:
        return bool(re.fullmatch(r"[A-Za-z0-9_]{3,32}", username))

    @staticmethod
    def _default_settings() -> dict:
        return {
            "theme": DEFAULT_THEME,
            "sound_enabled": DEFAULT_SOUND,
            "language": DEFAULT_LANGUAGE,
            "default_questions": DEFAULT_QUESTIONS,
            "default_duration": DEFAULT_DURATION_MINUTES,
        }
