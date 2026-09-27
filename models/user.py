"""User domain model."""

from dataclasses import dataclass


@dataclass
class User:
    id: int
    username: str
    display_name: str
