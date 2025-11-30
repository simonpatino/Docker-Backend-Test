from collections.abc import Sequence

from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select, text

from app.core.database import engine
from app.core.security import get_current_user
from app.models.hero import Hero
from app.models.user import Users

router = APIRouter(prefix="/heroes", tags=["heroes"])


@router.post("/", response_model=Hero)
def create_hero(hero: Hero, current_user: Users = Depends(get_current_user)) -> Hero:
    """Create a new hero."""
    with Session(engine) as session:
        session.add(hero)
        session.commit()
        session.refresh(hero)
        return hero


@router.get("/", response_model=Sequence[Hero])
def read_heroes(current_user: Users = Depends(get_current_user)) -> Sequence[Hero]:
    """Get all heroes."""
    with Session(engine) as session:
        heroes = session.exec(select(Hero)).all()
        return heroes


@router.get("/{hero_id}", response_model=Hero)
def read_hero(hero_id: int, current_user: Users = Depends(get_current_user)) -> Hero:
    """Get a hero by ID."""
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        if not hero:
            raise HTTPException(status_code=404, detail="Hero not found")
        return hero


@router.put("/{hero_id}", response_model=Hero)
def update_hero(
    hero_id: int, updated_hero: Hero, current_user: Users = Depends(get_current_user)
) -> Hero:
    """Update a hero."""
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        if not hero:
            raise HTTPException(status_code=404, detail="Hero not found")
        hero.name = updated_hero.name
        hero.secret_name = updated_hero.secret_name
        hero.age = updated_hero.age
        session.add(hero)
        session.commit()
        session.refresh(hero)
        return hero


@router.delete("/{hero_id}", response_model=dict)
def delete_hero(hero_id: int, current_user: Users = Depends(get_current_user)) -> dict:
    """Delete a hero."""
    with Session(engine) as session:
        hero = session.get(Hero, hero_id)
        if not hero:
            raise HTTPException(status_code=404, detail="Hero not found")

        hero_name = hero.name
        session.delete(hero)
        session.commit()
        return {"status": f"deleted {hero_name}"}
