"""Test session lifecycle and persistence."""

from __future__ import annotations

import json
import logging
from sqlalchemy import select
from sqlalchemy.orm import Session

from database.repositories.answer_repo import AnswerRecord
from database.repositories.test_result_repo import TestResultRecord
from database.repositories.test_session_repo import TestSessionRecord
from models.question import Question
from models.test_result import TestResultData
from models.test_session import TestSession, TestSessionStatus
from services.question_service import QuestionService, QuestionServiceError
from services.scoring_service import ScoringService

logger = logging.getLogger(__name__)


class TestService:
    def __init__(
        self,
        db: Session,
        question_service: QuestionService | None = None,
        scoring_service: ScoringService | None = None,
    ) -> None:
        self.db = db
        self.question_service = question_service or QuestionService()
        self.scoring_service = scoring_service or ScoringService()
        self._active_session: TestSession | None = None

    @property
    def active_session(self) -> TestSession | None:
        return self._active_session

    def create_session(
        self,
        user_id: int,
        topic: str,
        question_count: int,
        duration_minutes: int,
        points_per_question: int = 1,
    ) -> TestSession:
        try:
            questions = self.question_service.fetch_questions(topic, question_count)
        except QuestionServiceError:
            raise

        session = TestSession(
            topic=topic,
            questions=questions,
            duration_minutes=duration_minutes,
            points_per_question=points_per_question,
            user_id=user_id,
        )
        self._active_session = session
        return session

    def start_session(self, session: TestSession) -> None:
        session.start()
        self._active_session = session

    def submit_session(
        self, session: TestSession, expired: bool = False
    ) -> TestResultData:
        if session.status in (
            TestSessionStatus.COMPLETED,
            TestSessionStatus.EXPIRED,
        ):
            return self.scoring_service.evaluate(session)

        session.complete(expired=expired)
        result = self.scoring_service.evaluate(session)
        self._persist_result(session, result)
        self._active_session = None
        return result

    def _persist_result(self, session: TestSession, result: TestResultData) -> None:
        try:
            questions_json = json.dumps(
                [
                    {
                        "id": q.id,
                        "category": q.category,
                        "difficulty": q.difficulty,
                        "question": q.question,
                        "options": q.options,
                        "correct_answer": q.correct_answer,
                    }
                    for q in session.questions
                ]
            )

            session_record = TestSessionRecord(
                session_uuid=session.id,
                user_id=session.user_id or 0,
                topic=session.topic,
                duration_minutes=session.duration_minutes,
                total_questions=session.total_questions,
                status=session.status.value,
                start_time=session.start_time,
                end_time=session.end_time,
                questions_json=questions_json,
            )
            self.db.add(session_record)
            self.db.flush()

            result_record = TestResultRecord(
                session_id=session_record.id,
                user_id=session.user_id or 0,
                topic=result.topic,
                correct=result.correct,
                incorrect=result.incorrect,
                unanswered=result.unanswered,
                score=result.score,
                max_score=result.max_score,
                percentage=result.percentage,
                completed_at=result.completed_at,
            )
            self.db.add(result_record)
            self.db.flush()

            for item in result.review_items:
                self.db.add(
                    AnswerRecord(
                        result_id=result_record.id,
                        question_id=item.question_id,
                        question_text=item.question_text,
                        options_json=json.dumps(item.options),
                        user_answer=item.user_answer,
                        correct_answer=item.correct_answer,
                        is_correct=item.is_correct,
                        is_unanswered=item.is_unanswered,
                    )
                )

            self.db.commit()
            result.db_id = result_record.id
        except Exception as exc:
            logger.error("Failed to persist test result: %s", exc)
            self.db.rollback()

    def get_history(self, user_id: int) -> list[dict]:
        rows = self.db.execute(
            select(
                TestResultRecord.id,
                TestResultRecord.topic,
                TestResultRecord.percentage,
                TestResultRecord.score,
                TestResultRecord.max_score,
                TestResultRecord.completed_at,
                TestSessionRecord.session_uuid,
            )
            .join(
                TestSessionRecord,
                TestResultRecord.session_id == TestSessionRecord.id,
            )
            .where(TestResultRecord.user_id == user_id)
            .order_by(TestResultRecord.completed_at.desc())
        ).all()

        return [
            {
                "id": row.id,
                "topic": row.topic,
                "percentage": row.percentage,
                "score": row.score,
                "max_score": row.max_score,
                "date": row.completed_at,
                "session_uuid": row.session_uuid,
            }
            for row in rows
        ]

    def load_result(self, result_id: int, user_id: int) -> TestResultData | None:
        result_record = self.db.scalar(
            select(TestResultRecord).where(
                TestResultRecord.id == result_id,
                TestResultRecord.user_id == user_id,
            )
        )
        if not result_record:
            return None

        session_record = self.db.scalar(
            select(TestSessionRecord).where(
                TestSessionRecord.id == result_record.session_id
            )
        )
        if not session_record:
            return None

        answer_rows = self.db.scalars(
            select(AnswerRecord).where(AnswerRecord.result_id == result_record.id)
        ).all()

        answers = [
            {
                "question_id": a.question_id,
                "question_text": a.question_text,
                "options": json.loads(a.options_json),
                "user_answer": a.user_answer,
                "correct_answer": a.correct_answer,
                "is_correct": a.is_correct,
                "is_unanswered": a.is_unanswered,
            }
            for a in answer_rows
        ]

        return self.scoring_service.build_review_from_stored(
            questions=[],
            answers=answers,
            topic=result_record.topic,
            session_id=session_record.session_uuid,
            duration_minutes=session_record.duration_minutes,
            correct=result_record.correct,
            incorrect=result_record.incorrect,
            unanswered=result_record.unanswered,
            score=result_record.score,
            max_score=result_record.max_score,
            percentage=result_record.percentage,
        )
