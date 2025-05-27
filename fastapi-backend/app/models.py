import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .models import District, Hospital, User, Item

class TimestampMixin(SQLModel):
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

# Base models for API schemas
class ProvinceBase(SQLModel):
    name: str = Field(max_length=255)

class DistrictBase(SQLModel):
    name: str = Field(max_length=255)
    province_id: uuid.UUID = Field(foreign_key="province.id", nullable=False)

class HospitalBase(SQLModel):
    name: str = Field(max_length=255)
    district_id: uuid.UUID = Field(foreign_key="district.id", nullable=False)

class UserBase(SQLModel):
    email: EmailStr = Field(index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)

class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)

# Database models
class Province(ProvinceBase, table=True):
    __tablename__ = "province"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    districts: List["District"] = Relationship(back_populates="province", sa_relationship_kwargs={"lazy": "selectin"})

class District(DistrictBase, table=True):
    __tablename__ = "district"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    province: "Province" = Relationship(back_populates="districts", sa_relationship_kwargs={"lazy": "selectin"})
    hospitals: List["Hospital"] = Relationship(back_populates="district", sa_relationship_kwargs={"lazy": "selectin"})

class Hospital(HospitalBase, table=True):
    __tablename__ = "hospital"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    district: "District" = Relationship(back_populates="hospitals", sa_relationship_kwargs={"lazy": "selectin"})
    users: List["User"] = Relationship(back_populates="hospital", sa_relationship_kwargs={"lazy": "selectin"})

class User(UserBase, TimestampMixin, table=True):
    __tablename__ = "user"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    hospital_id: uuid.UUID = Field(foreign_key="hospital.id", nullable=False)
    hospital: "Hospital" = Relationship(back_populates="users", sa_relationship_kwargs={"lazy": "selectin"})
    items: List["Item"] = Relationship(back_populates="owner", cascade_delete=True, sa_relationship_kwargs={"lazy": "selectin"})

class Item(ItemBase, table=True):
    __tablename__ = "item"
    
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(foreign_key="user.id", nullable=False, ondelete="CASCADE")
    owner: "User" = Relationship(back_populates="items", sa_relationship_kwargs={"lazy": "selectin"})

# API schemas for creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=40)
    hospital_id: uuid.UUID = Field(foreign_key="hospital.id", nullable=False)

class UserRegister(SQLModel):
    email: EmailStr = Field(index=True, max_length=255)
    password: str = Field(min_length=8, max_length=40)
    full_name: str | None = Field(default=None, max_length=255)
    hospital_id: uuid.UUID = Field(foreign_key="hospital.id", nullable=False)

class ItemCreate(ItemBase):
    pass

# API schemas for update
class UserUpdate(UserBase):
    email: EmailStr | None = Field(default=None, max_length=255)  # type: ignore
    password: str | None = Field(default=None, min_length=8, max_length=40)

class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)

class ItemUpdate(ItemBase):
    title: str | None = Field(default=None, min_length=1, max_length=255)  # type: ignore

# API schemas for response
class ProvincePublic(ProvinceBase):
    id: uuid.UUID

class DistrictPublic(DistrictBase):
    id: uuid.UUID

class HospitalPublic(HospitalBase):
    id: uuid.UUID

class UserPublic(UserBase):
    id: uuid.UUID

class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID

# List response schemas
class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int

class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int

# Other schemas
class Message(SQLModel):
    message: str

class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(SQLModel):
    sub: str | None = None

class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=40)
    new_password: str = Field(min_length=8, max_length=40)

class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=40)
