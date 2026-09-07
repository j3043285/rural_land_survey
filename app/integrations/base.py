from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional

class BaseLandRecordProvider(ABC):
    """
    Standard interface for land record providers.
    Allows seamless switching between local demo provider and official
    Maharashtra government land record services (Mahabhulekh / Mahabhumi).
    """

    @abstractmethod
    def get_districts(self) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_talukas(self, district_id: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_villages(self, taluka_id: int) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def search_land_records(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_parcel_details(self, parcel_id: str) -> Optional[Dict[str, Any]]:
        pass

    @abstractmethod
    def get_land_map(self, parcel_id: str) -> Optional[Dict[str, Any]]:
        pass
