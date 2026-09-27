"""Internal question model — independent of external API format."""

from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class Question:
    id: str
    category: str
    difficulty: str
    question: str
    options: list[str]
    correct_answer: str

    @classmethod
    def create(
        cls,
        category: str,
        difficulty: str,
        question: str,
        options: list[str],
        correct_answer: str,
        question_id: str | None = None,
    ) -> "Question":
        return cls(
            id=question_id or str(uuid4()),
            category=category,
            difficulty=difficulty,
            question=question,
            options=list(options),
            correct_answer=correct_answer,
        )
