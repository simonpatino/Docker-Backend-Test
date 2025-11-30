from sqlmodel import SQLModel, Field
from pydantic import BaseModel, field_validator


class Users(SQLModel, table=True):
    """User database model."""
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str


class UserCreate(BaseModel):
    """Schema for creating a new user."""
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


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Schema for token response."""
    access_token: str
    token_type: str = "bearer"
