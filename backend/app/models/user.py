"""
User model and schemas.
"""

import uuid
from typing import TYPE_CHECKING, List
from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

from .mixins import TimestampMixin

if TYPE_CHECKING:
    from .hospital import Hospital
    from .item import Item


class UserBase(SQLModel):
    """Base user schema."""
    email: EmailStr = Field(index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


class User(UserBase, TimestampMixin, table=True):
    """User database model."""
    __tablename__ = "user"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    hospital_id: uuid.UUID = Field(foreign_key="hospital.id", nullable=False)
    hospital: "Hospital" = Relationship(
        back_populates="users", 
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    items: List["Item"] = Relationship(
        back_populates="owner", 
        cascade_delete=True, 
        sa_relationship_kwargs={"lazy": "selectin"}
    )


class UserCreate(UserBase):
    """User creation schema."""
    password: str = Field(min_length=8, max_length=40)
    hospital_id: uuid.UUID = Field(foreign_key="hospital.id", nullable=False)


class UserRegister(SQLModel):
    """User registration schema."""
    email: EmailStr = Field(index=True, max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)
    hospital_id: uuid.UUID = Field(foreign_key="hospital.id", nullable=False)


class UserUpdate(UserBase):
    """User update schema."""
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)


class UserUpdateMe(SQLModel):
    """User self-update schema."""
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UserPublic(UserBase):
    """User public API schema."""
    id: uuid.UUID


class UsersPublic(SQLModel):
    """Users list response schema."""
    data: list[UserPublic]
    count: int