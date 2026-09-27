"""SQLAlchemy database setup and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import DATABASE_URL

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def init_db() -> None:
    from database.repositories import answer_repo  # noqa: F401
    from database.repositories import settings_repo  # noqa: F401
    from database.repositories import test_result_repo  # noqa: F401
    from database.repositories import test_session_repo  # noqa: F401
    from database.repositories import user_repo  # noqa: F401

    Base.metadata.create_all(bind=engine)


def get_session():
    return SessionLocal()
