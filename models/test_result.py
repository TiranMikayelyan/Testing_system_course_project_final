"""Test result data transfer object."""

from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class AnswerReviewItem:
    question_id: str
    question_text: str
    options: list[str]
    user_answer: str | None
    correct_answer: str
    is_correct: bool
    is_unanswered: bool


@dataclass
class TestResultData:
    session_id: str
    topic: str
    total: int
    correct: int
    incorrect: int
    unanswered: int
    score: int
    max_score: int
    percentage: float
    duration_minutes: int
    completed_at: datetime = field(default_factory=datetime.now)
    review_items: list[AnswerReviewItem] = field(default_factory=list)
    db_id: int | None = None
