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
# DATABASE
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# REGISTER
# =========================

@router.post("/register")
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):

    existing_user = db.query(models.Users).filter(
        models.Users.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already exists"
        )

    hashed_pw = hash_password(user.password)

    new_user = models.Users(
        username=user.username,
        email=user.email,
        password=hashed_pw,
        role="user"
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "message": "User Registered Successfully"
    }


# =========================
# LOGIN
# =========================

@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):

    user = db.query(models.Users).filter(
        models.Users.email == form_data.username
    ).first()

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid Email"
        )

    if not verify_password(
        form_data.password,
        user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid Password"
        )

    access_token = create_access_token(
        data={
            "sub": user.email
        }
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }


# =========================
# CREATE RESUME
# =========================

@router.post("/resume")
def create_resume(
    resume: schemas.ResumeCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    new_resume = models.Resume(
        title=resume.title,
        content=resume.content,
        owner_id=current_user.id
    )

    db.add(new_resume)
    db.commit()
    db.refresh(new_resume)

    return {
        "message": "Resume Created",
        "data": {
            "id": new_resume.id,
            "title": new_resume.title,
            "content": new_resume.content
        }
    }


# =========================
# GET ALL RESUMES
# =========================

@router.get("/resume")
def get_resumes(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    resumes = db.query(models.Resume).filter(
        models.Resume.owner_id == current_user.id
    ).all()

    return resumes


# =========================
# ADMIN ONLY
# =========================

@router.get("/admin/users")
def get_all_users(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):

    if current_user.role != "admin":
        raise HTTPException(
            status_code=403,
            detail="Admin only"
        )

    users = db.query(models.Users).all()

    return users