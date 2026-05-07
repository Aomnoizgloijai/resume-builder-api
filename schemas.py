from pydantic import BaseModel


# =========================
# Register
# =========================
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str


# =========================
# Login
# =========================
class LoginRequest(BaseModel):
    email: str
    password: str


# =========================
# Resume Create
# =========================
class ResumeCreate(BaseModel):
    full_name: str
    education: str
    skills: str
    experience: str