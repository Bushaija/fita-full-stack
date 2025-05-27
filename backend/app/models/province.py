"""
Province model and schemas.
"""

import uuid
from typing import TYPE_CHECKING, List
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .district import District


class ProvinceBase(SQLModel):
    """Base province schema."""
    name: str = Field(max_length=255)


class Province(ProvinceBase, table=True):
    """Province database model."""
    __tablename__ = "province"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    districts: List["District"] = Relationship(
        back_populates="province", 
        sa_relationship_kwargs={"lazy": "selectin"}
    )


class ProvincePublic(ProvinceBase):
    """Province public API schema."""
    id: uuid.UUID