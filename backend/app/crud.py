import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    Item, ItemCreate, User, UserCreate, UserUpdate, UserRegister,
    Province, District, Hospital
)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def create_user_from_registration(
    *, session: Session, user_register: UserRegister
) -> User:
    """Create user from registration data with hospital_id lookup"""
    db_obj = User.model_validate(
        user_register, 
        update={"hashed_password": get_password_hash(user_register.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def register_user_with_location(
    *, 
    session: Session,
    name: str,
    email: str,
    password: str,
    province_name: str,
    district_name: str,
    hospital_name: str
) -> User:
    """Register a user by resolving province, district, and hospital names to IDs"""
    
    # Find province by name (case-insensitive)
    province_stmt = select(Province).where(Province.name.ilike(f"%{province_name}%"))
    province = session.exec(province_stmt).first()
    if not province:
        raise ValueError(f"Province '{province_name}' not found")
    
    # Find district by name within the province
    district_stmt = select(District).where(
        District.name.ilike(f"%{district_name}%"),
        District.province_id == province.id
    )
    district = session.exec(district_stmt).first()
    if not district:
        raise ValueError(f"District '{district_name}' not found in province '{province_name}'")
    
    # Find hospital by name within the district
    hospital_stmt = select(Hospital).where(
        Hospital.name.ilike(f"%{hospital_name}%"),
        Hospital.district_id == district.id
    )
    hospital = session.exec(hospital_stmt).first()
    if not hospital:
        raise ValueError(f"Hospital '{hospital_name}' not found in district '{district_name}'")
    
    # Create user with resolved hospital_id
    user_register = UserRegister(
        full_name=name,
        email=email,
        password=password,
        hospital_id=hospital.id
    )
    
    return create_user_from_registration(session=session, user_register=user_register)


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user:
        return None
    if not verify_password(password, db_user.hashed_password):
        return None
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


# Helper functions for location data
# def get_all_provinces(*, session: Session) -> list[Province]:
#     """Get all provinces"""
#     statement = select(Province)
#     return list(session.exec(statement).all())


# def get_districts_by_province(*, session: Session, province_id: uuid.UUID) -> list[District]:
#     """Get all districts in a province"""
#     statement = select(District).where(District.province_id == province_id)
#     return list(session.exec(statement).all())


# def get_hospitals_by_district(*, session: Session, district_id: uuid.UUID) -> list[Hospital]:
#     """Get all hospitals in a district"""
#     statement = select(Hospital).where(Hospital.district_id == district_id)
#     return list(session.exec(statement).all())


# def get_province_by_name(*, session: Session, name: str) -> Province | None:
#     """Get province by name (case-insensitive partial match)"""
#     statement = select(Province).where(Province.name.ilike(f"%{name}%"))
#     return session.exec(statement).first()


# def get_district_by_name(*, session: Session, name: str, province_id: uuid.UUID) -> District | None:
#     """Get district by name within a specific province"""
#     statement = select(District).where(
#         District.name.ilike(f"%{name}%"),
#         District.province_id == province_id
#     )
#     return session.exec(statement).first()


# def get_hospital_by_name(*, session: Session, name: str, district_id: uuid.UUID) -> Hospital | None:
#     """Get hospital by name within a specific district"""
#     statement = select(Hospital).where(
#         Hospital.name.ilike(f"%{name}%"),
#         Hospital.district_id == district_id
#     )
#     return session.exec(statement).first()

# get hospital by email
def get_hospital_by_user_email(*, session: Session, email: str) -> Hospital | None:
    statement = (
        select(Hospital)
        .join(User, Hospital.id == User.hospital_id)
        .where(User.email == email.lower())
    )
    return session.exec(statement).first()