"""Test scoring and answer review logic."""

from models.question import Question
from models.test_result import AnswerReviewItem, TestResultData
from models.test_session import TestSession


class ScoringService:
    """Evaluates test sessions and produces result data."""

    def evaluate(self, session: TestSession) -> TestResultData:
        correct = 0
        incorrect = 0
        unanswered = 0
        review_items: list[AnswerReviewItem] = []

        for question in session.questions:
            user_answer = session.get_answer(question.id)
            is_unanswered = user_answer is None
            is_correct = (
                not is_unanswered
                and user_answer.strip().lower()
                == question.correct_answer.strip().lower()
            )

            if is_unanswered:
                unanswered += 1
            elif is_correct:
                correct += 1
            else:
                incorrect += 1

            review_items.append(
                AnswerReviewItem(
                    question_id=question.id,
                    question_text=question.question,
                    options=question.options,
                    user_answer=user_answer,
                    correct_answer=question.correct_answer,
                    is_correct=is_correct,
                    is_unanswered=is_unanswered,
                )
            )

        total = len(session.questions)
        score = correct * session.points_per_question
        max_score = total * session.points_per_question
        percentage = (correct / total * 100) if total else 0.0

        return TestResultData(
            session_id=session.id,
            topic=session.topic,
            total=total,
            correct=correct,
            incorrect=incorrect,
            unanswered=unanswered,
            score=score,
            max_score=max_score,
            percentage=round(percentage, 1),
            duration_minutes=session.duration_minutes,
            review_items=review_items,
        )

    def build_review_from_stored(
        self,
        questions: list[Question],
        answers: list[dict],
        topic: str,
        session_id: str,
        duration_minutes: int,
        correct: int,
        incorrect: int,
        unanswered: int,
        score: int,
        max_score: int,
        percentage: float,
    ) -> TestResultData:
        review_items = [
            AnswerReviewItem(
                question_id=a["question_id"],
                question_text=a["question_text"],
                options=a["options"],
                user_answer=a["user_answer"],
                correct_answer=a["correct_answer"],
                is_correct=a["is_correct"],
                is_unanswered=a["is_unanswered"],
            )
            for a in answers
        ]
        return TestResultData(
            session_id=session_id,
            topic=topic,
            total=len(questions),
            correct=correct,
            incorrect=incorrect,
            unanswered=unanswered,
            score=score,
            max_score=max_score,
            percentage=percentage,
            duration_minutes=duration_minutes,
            review_items=review_items,
        )
