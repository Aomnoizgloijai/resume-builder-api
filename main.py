from fastapi import FastAPI

import models
from database import engine
from fastapi.middleware.cors import CORSMiddleware

from routers import users

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)

app.include_router(users.router)


@app.get("/")
def home():
    return {"message": "Resume Builder API Running"}