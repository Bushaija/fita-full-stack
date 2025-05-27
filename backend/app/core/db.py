import json
from collections import defaultdict
from pathlib import Path

from sqlmodel import Session, create_engine, select

from app import crud
from app.core.config import settings
from app.models import User, UserCreate, Province, District, Hospital

engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


# make sure all SQLModel models are imported (app.models) before initializing DB
# otherwise, SQLModel might fail to initialize relationships properly
# for more details: https://github.com/fastapi/full-stack-fastapi-template/issues/28


def init_db(session: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next lines
    # from sqlmodel import SQLModel

    # This works because the models are already imported and registered from app.models
    # SQLModel.metadata.create_all(engine)

    # user = session.exec(
    #     select(User).where(User.email == settings.FIRST_SUPERUSER)
    # ).first()
    # if not user:
    #     user_in = UserCreate(
    #         email=settings.FIRST_SUPERUSER,
    #         password=settings.FIRST_SUPERUSER_PASSWORD,
    #         is_superuser=True,
    #     )
    #     user = crud.create_user(session=session, user_create=user_in)

    # load seed data
    # Load JSON data
    seed_file = Path("app/data/province_district_hospitals.json")
    if not seed_file.exists():
        print("Seed file not found:", seed_file)
        return

    with open(seed_file, "r") as f:
        data = json.load(f)

    for entry in data:
        province_name = entry["province"].strip().lower()
        district_name = entry["district"].strip().lower()
        hospital_name = entry["hospital"].strip().lower()

        # 1. Province
        province = session.exec(
            select(Province).where(Province.name == province_name)
        ).first()
        if not province:
            province = Province(name=province_name)
            session.add(province)
            session.commit()
            session.refresh(province)

        # 2. District
        district = session.exec(
            select(District).where(
                District.name == district_name,
                District.province_id == province.id,
            )
        ).first()
        if not district:
            district = District(name=district_name, province_id=province.id)
            session.add(district)
            session.commit()
            session.refresh(district)

        # 3. Hospital
        hospital = session.exec(
            select(Hospital).where(
                Hospital.name == hospital_name,
                Hospital.district_id == district.id,
            )
        ).first()
        if not hospital:
            hospital = Hospital(name=hospital_name, district_id=district.id)
            session.add(hospital)

    session.commit()
    print("✅ Provinces, districts, and hospitals seeded successfully.")

   
