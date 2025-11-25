from fastapi import APIRouter, HTTPException
from sqlmodel import Field, Session, SQLModel, select
from pydantic import BaseModel, field_validator
from passlib.context import CryptContext
from app import engine
from jose import JWTError, jwt
from config import settings
from datetime import datetime, timedelta, timezone


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


routerSession = APIRouter()


class Users(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str

class UserCreate(BaseModel):
    username: str
    password: str

    @field_validator("password")
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        return v

    @field_validator("username")
    def username_not_empty(cls, v):
        if not v or v.strip() == "":
            raise ValueError("Username cannot be empty")
        return v

class userLogin(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Users

@routerSession.post("/register/", response_model=Users)
def create_user(user_data: UserCreate) -> Users:
    with Session(engine) as session:
        existing_user = session.exec(
            select(Users).where(Users.username == user_data.username)
        ).first()

        if existing_user:
            raise HTTPException(status_code=400, detail="Username already existing")

        hashed_pw = hash_password(user_data.password)
        user = Users(username=user_data.username, hashed_password=hashed_pw)
        session.add(user)
        session.commit()
        session.refresh(user)

        return user


@routerSession.post("/login/", response_model= TokenResponse)
def login_user(login_data: userLogin) -> dict:
    with Session(engine) as session:
        user = session.exec(
            select(Users).where(Users.username == login_data.username)
        ).first()

        if not user or not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        expire =datetime.now(timezone.utc) + timedelta(hours=1)

        payload = {"sub": user.username, "exp": expire}

        token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")

        return TokenResponse(access_token=token, user=user)