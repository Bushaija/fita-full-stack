"""
Item model and schemas.
"""

import uuid
from typing import TYPE_CHECKING
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User


class ItemBase(SQLModel):
    """Base item schema."""
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


class Item(ItemBase, table=True):
    """Item database model."""
    __tablename__ = "item"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    owner: "User" = Relationship(
        back_populates="items", 
        sa_relationship_kwargs={"lazy": "selectin"}
    )


class ItemCreate(ItemBase):
    """Item creation schema."""
    pass


class ItemUpdate(ItemBase):
    """Item update schema."""
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore


class ItemPublic(ItemBase):
    """Item public API schema."""
    id: uuid.UUID
    owner_id: uuid.UUID


class ItemsPublic(SQLModel):
    """Items list response schema."""
    data: list[ItemPublic]
    count: int