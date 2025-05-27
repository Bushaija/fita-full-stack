import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import col, delete, func, select

from app import crud
from app.api.deps import (
    CurrentUser,
    SessionDep,
    get_current_active_superuser,
)
from app.core.config import settings
from app.core.security import get_password_hash, verify_password
from app.models import (
    Item,
    Message,
    UpdatePassword,
    User,
    UserPublic,
    UsersPublic,
    UserUpdate,
    UserUpdateMe,
)
from app.utils import generate_new_account_email, send_email

router = APIRouter(prefix="/users", tags=["users"])


# Pydantic models for frontend signup request
class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    confirmPassword: str
    province: str
    district: str
    hospital: str


class LoginRequest(BaseModel):
    email: str
    password: str


# Response models for location data
class ProvinceResponse(BaseModel):
    id: str
    name: str


class DistrictResponse(BaseModel):
    id: str
    name: str
    province_id: str


class HospitalResponse(BaseModel):
    id: str
    name: str
    district_id: str



@router.post("/signup", response_model=UserPublic)
def register_user(session: SessionDep, signup_data: SignupRequest) -> Any:
    """
    Create new user without the need to be logged in.
    Handles frontend signup format with province/district/hospital names.
    """
    # Validate password confirmation
    print("signup data:", signup_data)
    if signup_data.password != signup_data.confirmPassword:
        raise HTTPException(
            status_code=400,
            detail="Password and confirm password do not match"
        )
    
    # Check if user already exists
    user = crud.get_user_by_email(session=session, email=signup_data.email)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    
    try:
        # Register user with location resolution
        user = crud.register_user_with_location(
            session=session,
            name=signup_data.name,
            email=signup_data.email,
            password=signup_data.password,
            province_name=signup_data.province,
            district_name=signup_data.district,
            hospital_name=signup_data.hospital
        )
        return user
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UsersPublic,
)
def read_users(session: SessionDep, skip: int = 0, limit: int = 100) -> Any:
    """
    Retrieve users.
    """
    count_statement = select(func.count()).select_from(User)
    count = session.exec(count_statement).one()

    statement = select(User).offset(skip).limit(limit)
    users = session.exec(statement).all()

    return UsersPublic(data=users, count=count)


# @router.post(
#     "/", dependencies=[Depends(get_current_active_superuser)], response_model=UserPublic
# )
# def create_user(*, session: SessionDep, user_in: UserCreate) -> Any:
#     """
#     Create new user.
#     """
#     user = crud.get_user_by_email(session=session, email=user_in.email)
#     if user:
#         raise HTTPException(
#             status_code=400,
#             detail="The user with this email already exists in the system.",
#         )

#     user = crud.create_user(session=session, user_create=user_in)
#     if settings.emails_enabled and user_in.email:
#         email_data = generate_new_account_email(
#             email_to=user_in.email, username=user_in.email, password=user_in.password
#         )
#         send_email(
#             email_to=user_in.email,
#             subject=email_data.subject,
#             html_content=email_data.html_content,
#         )
#     return user


@router.patch("/me", response_model=UserPublic)
def update_user_me(
    *, session: SessionDep, user_in: UserUpdateMe, current_user: CurrentUser
) -> Any:
    """
    Update own user.
    """
    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != current_user.id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )
    user_data = user_in.model_dump(exclude_unset=True)
    current_user.sqlmodel_update(user_data)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    return current_user


@router.patch("/me/password", response_model=Message)
def update_password_me(
    *, session: SessionDep, body: UpdatePassword, current_user: CurrentUser
) -> Any:
    """
    Update own password.
    """
    if not verify_password(body.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    if body.current_password == body.new_password:
        raise HTTPException(
            status_code=400, detail="New password cannot be the same as the current one"
        )
    hashed_password = get_password_hash(body.new_password)
    current_user.hashed_password = hashed_password
    session.add(current_user)
    session.commit()
    return Message(message="Password updated successfully")


@router.get("/me", response_model=UserPublic)
def read_user_me(current_user: CurrentUser) -> Any:
    """
    Get current user.
    """
    return current_user


@router.delete("/me", response_model=Message)
def delete_user_me(session: SessionDep, current_user: CurrentUser) -> Any:
    """
    Delete own user.
    """
    if current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    session.delete(current_user)
    session.commit()
    return Message(message="User deleted successfully")





# @router.post("/register", response_model=UserPublic)
# def register_user_legacy(session: SessionDep, user_in: UserRegister) -> Any:
#     """
#     Legacy registration endpoint for UserRegister model.
#     Kept for backward compatibility.
#     """
#     user = crud.get_user_by_email(session=session, email=user_in.email)
#     if user:
#         raise HTTPException(
#             status_code=400,
#             detail="The user with this email already exists in the system",
#         )
#     user_create = UserCreate.model_validate(user_in)
#     user = crud.create_user(session=session, user_create=user_create)
#     return user


# Location data endpoints for frontend dropdowns
# @router.get("/locations/provinces", response_model=list[ProvinceResponse])
# def get_provinces(session: SessionDep) -> Any:
#     """
#     Get all provinces for dropdown population.
#     """
#     provinces = crud.get_all_provinces(session=session)
#     return [
#         ProvinceResponse(id=str(province.id), name=province.name)
#         for province in provinces
#     ]


# @router.get("/locations/districts/{province_id}", response_model=list[DistrictResponse])
# def get_districts_by_province(province_id: str, session: SessionDep) -> Any:
#     """
#     Get all districts in a specific province.
#     """
#     try:
#         province_uuid = uuid.UUID(province_id)
#         districts = crud.get_districts_by_province(session=session, province_id=province_uuid)
#         return [
#             DistrictResponse(
#                 id=str(district.id),
#                 name=district.name,
#                 province_id=str(district.province_id)
#             )
#             for district in districts
#         ]
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid province ID format")


@router.get("/locations/hospitals/{district_id}", response_model=list[HospitalResponse])
def get_hospitals_by_district(district_id: str, session: SessionDep) -> Any:
    """
    Get all hospitals in a specific district.
    """
    try:
        district_uuid = uuid.UUID(district_id)
        hospitals = crud.get_hospitals_by_district(session=session, district_id=district_uuid)
        return [
            HospitalResponse(
                id=str(hospital.id),
                name=hospital.name,
                district_id=str(hospital.district_id)
            )
            for hospital in hospitals
        ]
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid district ID format")


@router.get("/{user_id}", response_model=UserPublic)
def read_user_by_id(
    user_id: uuid.UUID, session: SessionDep, current_user: CurrentUser
) -> Any:
    """
    Get a specific user by id.
    """
    user = session.get(User, user_id)
    if user == current_user:
        return user
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403,
            detail="The user doesn't have enough privileges",
        )
    return user


@router.patch(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserPublic,
)
def update_user(
    *,
    session: SessionDep,
    user_id: uuid.UUID,
    user_in: UserUpdate,
) -> Any:
    """
    Update a user.
    """
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user_in.email:
        existing_user = crud.get_user_by_email(session=session, email=user_in.email)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(
                status_code=409, detail="User with this email already exists"
            )

    db_user = crud.update_user(session=session, db_user=db_user, user_in=user_in)
    return db_user


@router.delete("/{user_id}", dependencies=[Depends(get_current_active_superuser)])
def delete_user(
    session: SessionDep, current_user: CurrentUser, user_id: uuid.UUID
) -> Message:
    """
    Delete a user.
    """
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        raise HTTPException(
            status_code=403, detail="Super users are not allowed to delete themselves"
        )
    statement = delete(Item).where(col(Item.owner_id) == user_id)
    session.exec(statement)  # type: ignore
    session.delete(user)
    session.commit()
    return Message(message="User deleted successfully")