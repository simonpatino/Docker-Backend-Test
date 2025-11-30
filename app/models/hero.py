from sqlmodel import SQLModel, Field


class Hero(SQLModel, table=True):
    """Hero database model."""
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)
