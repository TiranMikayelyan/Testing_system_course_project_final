"""Fetch and normalize questions from Open Trivia DB."""

from __future__ import annotations

import html
import logging
import random
from typing import Any

import requests

from config import (
    API_TIMEOUT,
    OPENTDB_BASE_URL,
    TOPIC_CATEGORY_MAP,
    USE_FALLBACK_ON_ERROR,
)
from models.question import Question

logger = logging.getLogger(__name__)


class QuestionServiceError(Exception):
    """Raised when questions cannot be loaded."""


# Small demo fallback — clearly separated from API questions
FALLBACK_QUESTIONS: list[dict[str, Any]] = [
    {
        "category": "Programming",
        "difficulty": "easy",
        "question": "What does HTML stand for?",
        "options": [
            "Hyper Text Markup Language",
            "High Tech Modern Language",
            "Home Tool Markup Language",
            "Hyperlinks Text Mark Language",
        ],
        "correct_answer": "Hyper Text Markup Language",
    },
    {
        "category": "Computer Science",
        "difficulty": "easy",
        "question": "Which data structure uses FIFO?",
        "options": ["Stack", "Queue", "Tree", "Graph"],
        "correct_answer": "Queue",
    },
    {
        "category": "Mathematics",
        "difficulty": "easy",
        "question": "What is 2 + 2?",
        "options": ["3", "4", "5", "22"],
        "correct_answer": "4",
    },
    {
        "category": "General Knowledge",
        "difficulty": "easy",
        "question": "What is the capital of France?",
        "options": ["London", "Berlin", "Paris", "Madrid"],
        "correct_answer": "Paris",
    },
    {
        "category": "Physics",
        "difficulty": "medium",
        "question": "What is the SI unit of force?",
        "options": ["Joule", "Newton", "Watt", "Pascal"],
        "correct_answer": "Newton",
    },
]


class QuestionService:
    """Communicates with Open Trivia DB and normalizes responses."""

    def __init__(self, timeout: int = API_TIMEOUT) -> None:
        self.timeout = timeout

    def fetch_questions(
        self,
        topic: str,
        count: int,
        difficulty: str | None = None,
    ) -> list[Question]:
        if count < 1:
            raise QuestionServiceError("Question count must be at least 1.")

        try:
            return self._fetch_from_api(topic, count, difficulty)
        except QuestionServiceError:
            if USE_FALLBACK_ON_ERROR:
                logger.warning("API failed — using demo fallback questions.")
                return self._fallback_questions(topic, count)
            raise

    def _fetch_from_api(
        self,
        topic: str,
        count: int,
        difficulty: str | None,
    ) -> list[Question]:
        params: dict[str, Any] = {
            "amount": count,
            "type": "multiple",
        }
        category_id = TOPIC_CATEGORY_MAP.get(topic)
        if category_id is not None:
            params["category"] = category_id
        if difficulty:
            params["difficulty"] = difficulty

        response = None
        last_error: QuestionServiceError | None = None
        for attempt in range(2):
            try:
                response = requests.get(
                    OPENTDB_BASE_URL, params=params, timeout=self.timeout
                )
                if response.status_code == 429:
                    logger.warning("API rate limit hit (attempt %d).", attempt + 1)
                    last_error = QuestionServiceError(
                        "API rate limit exceeded. Please wait a moment and try again."
                    )
                    continue
                response.raise_for_status()
                last_error = None
                break
            except requests.Timeout as exc:
                logger.error("API timeout: %s", exc)
                raise QuestionServiceError(
                    "Request timed out. Please check your Internet connection and try again."
                ) from exc
            except requests.ConnectionError as exc:
                logger.error("Connection error: %s", exc)
                raise QuestionServiceError(
                    "Unable to connect. Please check your Internet connection and try again."
                ) from exc
            except requests.RequestException as exc:
                logger.error("Request failed: %s", exc)
                raise QuestionServiceError(
                    "Unable to load questions. The quiz service may be unavailable."
                ) from exc

        if last_error or response is None:
            raise last_error or QuestionServiceError(
                "Unable to load questions. Please try again."
            )

        try:
            payload = response.json()
        except ValueError as exc:
            logger.error("Invalid JSON response")
            raise QuestionServiceError(
                "Received an invalid response from the quiz service."
            ) from exc

        if not isinstance(payload, dict):
            raise QuestionServiceError("Unexpected response format from quiz service.")

        response_code = payload.get("response_code")
        if response_code == 5:
            raise QuestionServiceError(
                "Too many questions requested. Please choose a smaller number."
            )
        if response_code != 0:
            raise QuestionServiceError(
                "Unable to load questions. Please try again later."
            )

        raw_questions = payload.get("results", [])
        if not raw_questions:
            raise QuestionServiceError(
                "No questions available for the selected topic."
            )

        questions = [self._normalize(item, topic) for item in raw_questions]
        if len(questions) < count:
            logger.warning(
                "API returned %d questions, requested %d", len(questions), count
            )
        return questions[:count]

    def _normalize(self, item: dict[str, Any], topic: str) -> Question:
        try:
            question_text = html.unescape(item["question"])
            correct = html.unescape(item["correct_answer"])
            incorrect = [html.unescape(a) for a in item["incorrect_answers"]]
            options = incorrect + [correct]
            random.shuffle(options)
            difficulty = item.get("difficulty", "medium")
            category = item.get("category", topic)
            category = html.unescape(category)
        except (KeyError, TypeError) as exc:
            raise QuestionServiceError("Invalid question data from API.") from exc

        return Question.create(
            category=category,
            difficulty=difficulty,
            question=question_text,
            options=options,
            correct_answer=correct,
        )

    def _fallback_questions(self, topic: str, count: int) -> list[Question]:
        pool = [
            q for q in FALLBACK_QUESTIONS if q["category"] == topic
        ] or FALLBACK_QUESTIONS
        selected: list[Question] = []
        for i in range(count):
            item = pool[i % len(pool)]
            options = list(item["options"])
            random.shuffle(options)
            selected.append(
                Question.create(
                    category=item["category"],
                    difficulty=item["difficulty"],
                    question=item["question"] + " [DEMO]",
                    options=options,
                    correct_answer=item["correct_answer"],
                )
            )
        return selected
