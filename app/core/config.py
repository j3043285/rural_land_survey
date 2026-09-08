import os
from typing import Optional


def _fix_database_url(url: str) -> str:
    """
    Render (and some older tools) emit postgres:// which SQLAlchemy 2.x no
    longer accepts.  Also ensure we use the psycopg2 driver so the existing
    psycopg2-binary dependency is picked up correctly.
    """
    if url.startswith("postgres://"):
        url = "postgresql+psycopg2://" + url[len("postgres://"):]
    elif url.startswith("postgresql://"):
        url = "postgresql+psycopg2://" + url[len("postgresql://"):]
    return url


class Settings:
    PROJECT_NAME: str = "LandSetu - Rural Agricultural Land Survey / Resurvey"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sih2026-rural-land-survey-secure-token-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day

    # Defaults to local SQLite; production should set DATABASE_URL env var
    # to the Render *Internal* Database URL (host ending in -a.internal or just -a).
    DATABASE_URL: str = _fix_database_url(
        os.getenv(
            "DATABASE_URL",
            f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../rural_land.db'))}"
        )
    )

    # Official Maharashtra integration toggle: 'mock' or 'official'
    LAND_DATA_PROVIDER: str = os.getenv("LAND_DATA_PROVIDER", "mock")
    OFFICIAL_LAND_API_URL: Optional[str] = os.getenv("OFFICIAL_LAND_API_URL", None)
    OFFICIAL_LAND_API_KEY: Optional[str] = os.getenv("OFFICIAL_LAND_API_KEY", None)

    # Uploads directory
    UPLOAD_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../uploads"))

    # Discrepancy boundary threshold in percentage (e.g. 2.0%)
    DISCREPANCY_THRESHOLD_PCT: float = 2.0


settings = Settings()

