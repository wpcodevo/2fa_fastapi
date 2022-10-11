from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app import auth

app = FastAPI()

origins = [
    settings.CLIENT_ORIGIN,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, tags=['Auth'], prefix='/api/auth')


@app.get("/api/healthchecker")
def root():
    return {"message": "Welcome to 2FA Authentication with FastAPI"}
