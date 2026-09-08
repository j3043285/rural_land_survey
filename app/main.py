import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import engine, Base, SessionLocal
import app.models  # Ensures all models are imported


def _auto_seed():
    """Seed Districts/Talukas/Villages from the bundled XLS workbook if the
    database is completely empty (e.g. a fresh Render PostgreSQL instance)."""
    from app.models.locations import Village

    db = SessionLocal()
    try:
        village_count = db.query(Village).count()
    finally:
        db.close()

    if village_count > 0:
        print(f"[seed] Database already has {village_count} villages — skipping auto-seed.")
        return

    # Locate the most recent XLS in the seed/ directory
    seed_dir = Path(__file__).resolve().parents[1] / "seed"
    xlsx_files = sorted(seed_dir.glob("*.xlsx"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not xlsx_files:
        print("[seed] No .xlsx file found in seed/ — skipping auto-seed.")
        return

    workbook = xlsx_files[0]
    print(f"[seed] Seeding from {workbook} …")

    # Ensure the project root is on the path so import_workbook can use app.*
    project_root = str(Path(__file__).resolve().parents[1])
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    try:
        from seed.import_villages import import_workbook
        import_workbook(workbook)
        print("[seed] Auto-seed complete.")
    except Exception as exc:
        print(f"[seed] WARNING: Auto-seed failed: {exc}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    _auto_seed()
    yield
    # Shutdown (nothing to clean up)


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="SIH 2026 Problem Statement SIH26010: Rural Agricultural Land Survey / Resurvey Platform",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount uploads static folder
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# Include Routers
from app.api import auth, locations, parcels, surveys, discrepancies, documents, reports, analytics, ai, system, grievances

app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(locations.router, prefix=settings.API_V1_STR)
app.include_router(parcels.router, prefix=settings.API_V1_STR)
app.include_router(surveys.router, prefix=settings.API_V1_STR)
app.include_router(discrepancies.router, prefix=settings.API_V1_STR)
app.include_router(documents.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(ai.router, prefix=settings.API_V1_STR)
app.include_router(system.router, prefix=settings.API_V1_STR)
app.include_router(grievances.router, prefix=settings.API_V1_STR)


@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "status": "online",
        "docs": "/api/docs",
        "land_data_provider": settings.LAND_DATA_PROVIDER,
        "mode": "Demonstration / Synthetic Evaluation Records"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
