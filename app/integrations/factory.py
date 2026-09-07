from app.core.config import settings
from app.integrations.base import BaseLandRecordProvider
from app.integrations.mock_provider import MockLandRecordProvider
from app.integrations.mahabhulekh_adapter import MahabhulekhAdapter

def get_land_record_provider() -> BaseLandRecordProvider:
    """
    Factory to resolve the active land record provider based on configuration.
    """
    if settings.LAND_DATA_PROVIDER.lower() == "official":
        return MahabhulekhAdapter()
    return MockLandRecordProvider()
