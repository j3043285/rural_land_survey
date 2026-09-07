from typing import List, Dict, Any, Optional
from app.integrations.base import BaseLandRecordProvider

class MockLandRecordProvider(BaseLandRecordProvider):
    """
    Development and testing provider utilizing clearly labelled synthetic DEMO data.
    Does not spoof official government signatures.
    """

    def get_districts(self) -> List[Dict[str, Any]]:
        return [
            {"id": 1, "name": "Nashik", "state": "Maharashtra", "code": "MH-NSK", "provider": "DEMO_DATA"}
        ]

    def get_talukas(self, district_id: int) -> List[Dict[str, Any]]:
        return [
            {"id": 1, "name": "Yeola", "district_id": 1, "code": "YLA", "provider": "DEMO_DATA"},
            {"id": 2, "name": "Nashik", "district_id": 1, "code": "NSK", "provider": "DEMO_DATA"},
            {"id": 3, "name": "Sinnar", "district_id": 1, "code": "SNR", "provider": "DEMO_DATA"},
            {"id": 4, "name": "Dindori", "district_id": 1, "code": "DND", "provider": "DEMO_DATA"},
            {"id": 5, "name": "Kalwan", "district_id": 1, "code": "KLW", "provider": "DEMO_DATA"}
        ]

    def get_villages(self, taluka_id: int) -> List[Dict[str, Any]]:
        return [
            {"id": 1, "name": "Pimpalgaon", "taluka_id": 1, "code": "PMP", "provider": "DEMO_DATA"},
            {"id": 2, "name": "Savargaon", "taluka_id": 1, "code": "SVG", "provider": "DEMO_DATA"},
            {"id": 3, "name": "Andarsul", "taluka_id": 1, "code": "ADL", "provider": "DEMO_DATA"}
        ]

    def search_land_records(self, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        return [
            {
                "survey_number": "50/1",
                "gat_number": "50/1",
                "owner_name": "Patil Shankar Bapu",
                "area_hectares": 1.82,
                "land_type": "Agricultural (Kharif)",
                "status": "Verified",
                "provider": "DEMO_DATA"
            }
        ]

    def get_parcel_details(self, parcel_id: str) -> Optional[Dict[str, Any]]:
        return {
            "survey_number": "50/1",
            "gat_number": "50/1",
            "area_hectares": 1.82,
            "area_acres": 4.50,
            "land_type": "Agricultural (Kharif)",
            "owner_name": "Patil Shankar Bapu",
            "khata_number": "1042",
            "boundary_status": "Verified",
            "discrepancy": "No Discrepancy",
            "remarks": "Boundary matched with GPS",
            "last_survey_date": "12 Apr 2025",
            "coordinates": {"lat": 19.1234, "lng": 74.4321},
            "provider": "DEMO_DATA"
        }

    def get_land_map(self, parcel_id: str) -> Optional[Dict[str, Any]]:
        return {
            "type": "Feature",
            "geometry": {
                "type": "Polygon",
                "coordinates": [[[74.4310, 19.1225], [74.4330, 19.1225], [74.4330, 19.1245], [74.4310, 19.1245], [74.4310, 19.1225]]]
            },
            "properties": {"survey_number": "50/1", "provider": "DEMO_DATA"}
        }
