from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from sqlmodel import Field, Session, SQLModel, create_engine, select, text

from config import settings


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)


engine = create_engine(str(settings.SQLALCHEMY_DATABASE_URI))


def create_db_and_tables() -> None:
    SQLModel.metadata.create_all(engine)


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
def hello() -> str:
    return "Hello, Docker!"


@app.post("/heroes/")
def create_hero(hero: Hero) -> Hero:
    with Session(engine) as session:
        session.add(hero)
        session.commit()
        session.refresh(hero)
        return hero


@app.get("/heroes/")
def read_heroes() -> Sequence[Hero]:
    with Session(engine) as session:
        heroes = session.exec(select(Hero)).all()
        return heroes


@app.get("/health/")
def health_check() -> dict:
    with Session(engine) as session:
        test = session.exec(select(1)).first()

        version = session.exec(text("SELECT VERSION();")).scalar_one()

        quantity = session.exec(text("SELECT COUNT(*) FROM hero;")).scalar_one()

        if test == 1:
            return {"status": "healthyy", "version": version, "hero_count": quantity}
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="unhealthy"
            )


@app.get("/heroes/{hero_id}")
def read_hero(hero_id: int) -> Hero:
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        if not hero:
            raise HTTPException(404)
        return hero


@app.put("/heroes/{hero_id}")
def update_hero(hero_id: int, updated_hero: Hero) -> Hero:
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        if not hero:
            raise HTTPException(404)
        hero.name = updated_hero.name
        hero.secret_name = updated_hero.secret_name
        hero.age = updated_hero.age
        session.add(hero)
        session.commit()
        session.refresh(hero)
        return hero


@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int) -> dict:
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)

        if not hero:
            raise HTTPException(404)

        hero_name = hero.name
        session.exec(text(f"DELETE FROM hero WHERE id = {hero_id}"))
        session.commit()
        return {"status": f"deleted {hero_name}"}
