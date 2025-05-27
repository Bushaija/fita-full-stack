"""
Hospital model and schemas.
"""

import uuid
from typing import TYPE_CHECKING, List
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .district import District
    from .user import User


class HospitalBase(SQLModel):
    """Base hospital schema."""
    name: str = Field(max_length=255)
    district_id: uuid.UUID = Field(foreign_key="district.id", nullable=False)


class Hospital(HospitalBase, table=True):
    """Hospital database model."""
    __tablename__ = "hospital"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    district: "District" = Relationship(
        back_populates="hospitals", 
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    users: List["User"] = Relationship(
        back_populates="hospital", 
        sa_relationship_kwargs={"lazy": "selectin"}
    )


class HospitalPublic(HospitalBase):
    """Hospital public API schema."""
    id: uuid.UUID