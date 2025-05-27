"""
Authentication related schemas.
"""

from sqlmodel import Field, SQLModel


class Token(SQLModel):
    """Token response schema."""
    access_token: str
    token_type: str = "bearer"


class TokenPayload(SQLModel):
    """Token payload schema."""
    sub: str | None = None


class UpdatePassword(SQLModel):
    """Password update schema."""
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)


class NewPassword(SQLModel):
    """New password schema for password reset."""
    token: str
    new_password: str = Field(min_length=8, max_length=40)