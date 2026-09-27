"""In-memory test session model."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from uuid import uuid4

from models.question import Question


class TestSessionStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"


@dataclass
class TestSession:
    topic: str
    questions: list[Question]
    duration_minutes: int
    points_per_question: int = 1
    id: str = field(default_factory=lambda: str(uuid4()))
    answers: dict[str, str | None] = field(default_factory=dict)
    start_time: datetime | None = None
    end_time: datetime | None = None
    status: TestSessionStatus = TestSessionStatus.PENDING
    user_id: int | None = None

    def __post_init__(self) -> None:
        if not self.answers:
            self.answers = {q.id: None for q in self.questions}

    @property
    def total_questions(self) -> int:
        return len(self.questions)

    @property
    def duration_seconds(self) -> int:
        return self.duration_minutes * 60

    def set_answer(self, question_id: str, answer: str | None) -> None:
        if self.status not in (TestSessionStatus.ACTIVE, TestSessionStatus.PENDING):
            return
        if question_id in self.answers:
            self.answers[question_id] = answer

    def get_answer(self, question_id: str) -> str | None:
        return self.answers.get(question_id)

    def answered_count(self) -> int:
        return sum(1 for a in self.answers.values() if a is not None)

    def start(self) -> None:
        self.start_time = datetime.now()
        self.status = TestSessionStatus.ACTIVE

    def complete(self, expired: bool = False) -> None:
        self.end_time = datetime.now()
        self.status = (
            TestSessionStatus.EXPIRED if expired else TestSessionStatus.COMPLETED
        )
