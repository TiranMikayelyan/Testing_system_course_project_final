"""User settings database repository."""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database.database import Base


class UserSettingsRecord(Base):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), unique=True, nullable=False
    )
    theme: Mapped[str] = mapped_column(String(32), default="dark")
    sound_enabled: Mapped[str] = mapped_column(String(8), default="true")
    language: Mapped[str] = mapped_column(String(8), default="en")
    default_questions: Mapped[int] = mapped_column(Integer, default=10)
    default_duration: Mapped[int] = mapped_column(Integer, default=15)
