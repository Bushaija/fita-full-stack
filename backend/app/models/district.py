"""
District model and schemas.
"""

import uuid
from typing import TYPE_CHECKING, List
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .province import Province
    from .hospital import Hospital


class DistrictBase(SQLModel):
    """Base district schema."""
    name: str = Field(max_length=255)
    province_id: uuid.UUID = Field(foreign_key="province.id", nullable=False)


class District(DistrictBase, table=True):
    """District database model."""
    __tablename__ = "district"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    province: "Province" = Relationship(
        back_populates="districts", 
        sa_relationship_kwargs={"lazy": "selectin"}
    )
    hospitals: List["Hospital"] = Relationship(
        back_populates="district", 
        sa_relationship_kwargs={"lazy": "selectin"}
    )


class DistrictPublic(DistrictBase):
    """District public API schema."""
    id: uuid.UUID