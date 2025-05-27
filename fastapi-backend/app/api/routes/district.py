import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import select

from app.api.deps import SessionDep
from app.models import Hospital, User, District


router = APIRouter(tags=["district"])

class HospitalResponse(BaseModel):
    id: uuid.UUID
    name: str
    district_id: uuid.UUID

# get hospital by email
# @router.get("/hospitals/{email}", response_model=HospitalResponse)
# def get_hospital_by_email(email: str, session: SessionDep):
#     """
#     Get hospital by email.
#     """
#     hospital = 
#     if not hospital:
#         raise HTTPException(status_code=404, detail="Hospital not found")
#     return hospital


# @router.get("/hospitals/by-email/{email}", response_model=HospitalResponse)
# def get_hospital_by_email(email: str, session: SessionDep):
#     hospital = session.exec(select(Hospital).where(User.email == email)).first()
#     if not hospital:
#         raise HTTPException(status_code=404, detail="Hospital not found")
#     return hospital

@router.get("/district/by-email/{email}", response_model=HospitalResponse)
def get_district_by_email(email: str, session: SessionDep):
    # Step 1: Find the user by email
    user = session.exec(select(User).where(User.email == email.lower())).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Step 2: Fetch the hospital using the user's hospital_id
    hospital = session.get(Hospital, user.hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")

    # step3: Fetch the district using hospital_id
    district = session.get(District, hospital.district_id)
    if not district:
        raise HTTPException(status_code=404, detail="District not found")

    return district



