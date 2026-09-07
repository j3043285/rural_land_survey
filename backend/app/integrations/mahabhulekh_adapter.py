import httpx
from typing import List, Dict, Any, Optional
from app.integrations.base import BaseLandRecordProvider
from app.core.config import settings

class MahabhulekhAdapter(BaseLandRecordProvider):
    """
    Official Maharashtra Mahabhulekh API adapter.
    Requires authorized government credentials (OFFICIAL_LAND_API_URL, OFFICIAL_LAND_API_KEY).
    Does NOT attempt to scrape or bypass government CAPTCHA.
    Uses authenticated enterprise REST/OAuth endpoints when available.
    """

    def __init__(self):
        self.base_url = settings.OFFICIAL_LAND_API_URL or "https://mahabhulekh.maharashtra.gov.in/api/v1"
        self.api_key = settings.OFFICIAL_LAND_API_KEY
        self.client = httpx.Client(timeout=10.0, headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {})

    def get_districts(self) -> List[Dict[str, Any]]:
        if not self.api_key:
            raise RuntimeError("Mahabhulekh official credentials not configured in environment.")
        response = self.client.get(f"{self.base_url}/districts")
        response.raise_for_status()
        return response.json()

    def get_talukas(self, district_id: int) -> List[Dict[str, Any]]:
        if not self.api_key:
            raise RuntimeError("Mahabhulekh official credentials not configured in environment.")
        response = self.client.get(f"{self.base_url}/talukas", params={"district_id": district_id})
        response.raise_for_status()
        return response.json()

    def get_villages(self, taluka_id: int) -> List[Dict[str, Any]]:
        if not self.api_key:
            raise RuntimeError("Mahabhulekh official credentials not configured in environment.")
        response = self.client.get(f"{self.base_url}/villages", params={"taluka_id": taluka_id})
        response.raise_for_status()
        return response.json()

    def search_land_records(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        if not self.api_key:
            raise RuntimeError("Mahabhulekh official credentials not configured in environment.")
        response = self.client.post(f"{self.base_url}/records/search", json=filters)
        response.raise_for_status()
        return response.json()

    def get_parcel_details(self, parcel_id: str) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            raise RuntimeError("Mahabhulekh official credentials not configured in environment.")
        response = self.client.get(f"{self.base_url}/parcels/{parcel_id}")
        response.raise_for_status()
        return response.json()

    def get_land_map(self, parcel_id: str) -> Optional[Dict[str, Any]]:
        if not self.api_key:
            raise RuntimeError("Mahabhulekh official credentials not configured in environment.")
        response = self.client.get(f"{self.base_url}/parcels/{parcel_id}/cadastral-map")
        response.raise_for_status()
        return response.json()
