import os
from typing import Optional

class Settings:
    PROJECT_NAME: str = "LandSetu - Rural Agricultural Land Survey / Resurvey"
    API_V1_STR: str = "/api"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sih2026-rural-land-survey-secure-token-key-2026")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    
    # Defaults to local SQLite if PostgreSQL is not configured; production can supply PostgreSQL URL
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL", 
        f"sqlite:///{os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../rural_land.db'))}"
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
