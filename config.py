import os
from typing import Any

from pydantic import (
    PostgresDsn,
    computed_field,
    field_validator,
    model_validator,
)
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    POSTGRES_SERVER: str
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str | None = None
    POSTGRES_PASSWORD_FILE: str | None = None
    POSTGRES_DB: str
    JWT_SECRET: str | None = None
    JWT_SECRET_FILE: str | None = None

    @model_validator(mode="before")
    @classmethod
    def check_postgres_password(cls, data: Any) -> Any:
        """Validate that either POSTGRES_PASSWORD or POSTGRES_PASSWORD_FILE is set."""
        if isinstance(data, dict):
            password_file: str | None = data.get("POSTGRES_PASSWORD_FILE")  # type: ignore
            password: str | None = data.get("POSTGRES_PASSWORD")  # type: ignore
            if password_file is None and password is None:
                raise ValueError(
                    "At least one of POSTGRES_PASSWORD_FILE and POSTGRES_PASSWORD must be set."
                )
        return data  # type: ignore

    @field_validator("POSTGRES_PASSWORD_FILE", mode="before")
    @classmethod
    def read_password_from_file(cls, v: str | None) -> str | None:
        if v is not None:
            file_path = v
            if os.path.exists(file_path):
                with open(file_path) as file:
                    return file.read().strip()
            raise ValueError(f"Password file {file_path} does not exist.")
        return v

    @model_validator(mode="before")
    @classmethod
    def check_jwt_secret(cls, data: Any) -> Any:
        """Validate that JWT_SECRET or JWT_SECRET_FILE is set."""
        if isinstance(data, dict):
            secret_file: str | None = data.get("JWT_SECRET_FILE")  # type: ignore
            secret: str | None = data.get("JWT_SECRET")  # type: ignore
            if secret_file is None and secret is None:
                raise ValueError(
                    "At least one of JWT_SECRET_FILE and JWT_SECRET must be set."
                )
        return data  # type: ignore

    @field_validator("JWT_SECRET_FILE", mode="before")
    @classmethod
    def read_jwt_secret_from_file(cls, v: str | None) -> str | None:
        if v is not None:
            file_path = v
            if os.path.exists(file_path):
                with open(file_path) as file:
                    return file.read().strip()
            raise ValueError(f"JWT secret file {file_path} does not exist.")
        return v

    @property
    def SECRET_KEY(self) -> str:
        return self.JWT_SECRET or self.JWT_SECRET_FILE
  

    @computed_field
    @property
    def SQLALCHEMY_DATABASE_URI(self) -> PostgresDsn:
        url = MultiHostUrl.build(
            scheme="postgresql+psycopg",
            username=self.POSTGRES_USER,
            password=self.POSTGRES_PASSWORD
            if self.POSTGRES_PASSWORD
            else self.POSTGRES_PASSWORD_FILE,
            host=self.POSTGRES_SERVER,
            port=self.POSTGRES_PORT,
            path=self.POSTGRES_DB,
        )
        return PostgresDsn(url)


settings = Settings()  # type: ignore
