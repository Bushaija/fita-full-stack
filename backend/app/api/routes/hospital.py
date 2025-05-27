import uuid

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.api.deps import SessionDep
from app.models import Hospital


router = APIRouter(tags=["hospitals"])

class HospitalResponse(BaseModel):
    id: uuid.UUID
    name: str
    district_id: uuid.UUID

# get hospital by email
@router.get("/hospitals/{hospital_id}", response_model=HospitalResponse)
def get_hospital_by_email(hospital_id: uuid.UUID, session: SessionDep):
    """
    Get hospital by hospital_id.
    """
    hospital = session.get(Hospital, hospital_id)
    if not hospital:
        raise HTTPException(status_code=404, detail="Hospital not found")
    return hospital


