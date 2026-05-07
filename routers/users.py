from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import models
import schemas

from database import SessionLocal
from auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user
)

router = APIRouter()


# =========================
# Database Connection
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# Register
# =========================
@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = models.User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        role=user.role
    )

    db.add(new_user)
    db.commit()

    return {"message": "User created successfully"}


# =========================
# Login
# =========================
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    db_user = db.query(models.User).filter(
        models.User.email == form_data.username
    ).first()

    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid email")

    if not verify_password(form_data.password, db_user.password):
        raise HTTPException(status_code=401, detail="Invalid password")

    access_token = create_access_token(
        data={
            "sub": db_user.email,
            "role": db_user.role
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# =========================
# Create Resume
# =========================
@router.post("/resume")
def create_resume(
    resume: schemas.ResumeCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    new_resume = models.Resume(
        full_name=resume.full_name,
        education=resume.education,
        skills=resume.skills,
        experience=resume.experience,
        owner_id=current_user.id
    )

    db.add(new_resume)
    db.commit()

    return {"message": "Resume created successfully"}


# =========================
# Get My Resume
# =========================
@router.get("/my-resume")
def get_my_resume(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    resumes = db.query(models.Resume).filter(
        models.Resume.owner_id == current_user.id
    ).all()

    return resumes


# =========================
# Admin Only
# =========================
@router.get("/admin/users")
def get_all_users(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Access denied")

    users = db.query(models.User).all()

    return users