from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from sqlmodel import Session, select, text

from app.core.database import engine, create_db_and_tables
from app.routers import heroes, auth


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncIterator[None]:
    """Application lifespan: startup and shutdown events."""
    # Startup: Create database tables
    create_db_and_tables()
    yield
    # Shutdown: Add cleanup logic here if needed


app = FastAPI(
    title="Heroes API",
    description="A FastAPI application with authentication and hero management",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(auth.router)
app.include_router(heroes.router)


@app.get("/", tags=["root"])
def root() -> dict:
    """Root endpoint."""
    return {"message": "Hello, Docker! Visit /docs for API documentation."}


@app.get("/health", tags=["health"])
def health_check() -> dict:
    """Health check endpoint."""
    with Session(engine) as session:
        test = session.exec(select(1)).first()
        version = session.exec(text("SELECT VERSION();")).scalar_one()
        quantity = session.exec(text("SELECT COUNT(*) FROM hero;")).scalar_one()

        if test == 1:
            return {"status": "healthy", "version": version, "hero_count": quantity}
        else:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="unhealthy"
            )
