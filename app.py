from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select, text
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from config import settings


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login/")


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

# includes ALL routers


from appSession import routerSession
from appSession import Users

app.include_router(routerSession)


def get_current_user(token: str = Depends(oauth2_scheme)) -> Users:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])

        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    with Session(engine) as session:
        user = session.exec(select(Users).where(Users.username == username)).first()
        if user is None:
            raise credentials_exception

    return user


@app.get("/")
def hello() -> str:
    return "Hello, Docker!"


@app.post("/heroes/", response_model=Hero)
def create_hero(hero: Hero, current_user: Users = Depends(get_current_user)) -> Hero:
    with Session(engine) as session:
        session.add(hero)
        session.commit()
        session.refresh(hero)
        return hero


@app.get("/heroes/")
def read_heroes(current_user: Users = Depends(get_current_user)) -> Sequence[Hero]:
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
def read_hero(hero_id: int, current_user: Users = Depends(get_current_user)) -> Hero:
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        if not hero:
            raise HTTPException(404)
        return hero


@app.put("/heroes/{hero_id}", response_model=Hero)
def update_hero(hero_id: int, updated_hero: Hero, current_user: Users = Depends(get_current_user)) -> Hero:
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


@app.delete("/heroes/{hero_id}", response_model=dict)
def delete_hero(hero_id: int, current_user: Users = Depends(get_current_user)) -> dict:
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)

        if not hero:
            raise HTTPException(404)

        hero_name = hero.name
        session.exec(text(f"DELETE FROM hero WHERE id = {hero_id}"))
        session.commit()
        return {"status": f"deleted {hero_name}"}
