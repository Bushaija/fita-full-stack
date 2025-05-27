"""
Model mixins for common functionality.
"""

from datetime import datetime
from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    """Mixin to add created_at and updated_at timestamps to models."""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)