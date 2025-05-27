"""
Common schemas used across the application.
"""

from sqlmodel import SQLModel


class Message(SQLModel):
    """Generic message response schema."""
    message: str