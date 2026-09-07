import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"

def test_locations_cascade():
    # 1. Districts
    res_dist = client.get("/api/districts")
    assert res_dist.status_code == 200
    districts = res_dist.json()
    assert len(districts) > 0
    nashik = next((d for d in districts if d["name"] == "Nashik"), None)
    assert nashik is not None

    # 2. Talukas
    res_tal = client.get(f"/api/talukas?district_id={nashik['id']}")
    assert res_tal.status_code == 200
    talukas = res_tal.json()
    yeola = next((t for t in talukas if t["name"] == "Yeola"), None)
    assert yeola is not None

    # 3. Villages
    res_vil = client.get(f"/api/villages?taluka_id={yeola['id']}")
    assert res_vil.status_code == 200
    villages = res_vil.json()
    pimpalgaon = next((v for v in villages if v["name"] == "Pimpalgaon"), None)
    assert pimpalgaon is not None

def test_parcels_search():
    # Search by 50/1
    res = client.get("/api/parcels/search?q=50/1")
    assert res.status_code == 200
    parcels = res.json()
    assert len(parcels) > 0
    assert any("50/1" in p["gat_number"] for p in parcels)

    # Search by owner name
    res_name = client.get("/api/parcels/search?q=Shankar")
    assert res_name.status_code == 200
    name_parcels = res_name.json()
    assert len(name_parcels) > 0
    assert any("Shankar" in p["owner_name"] for p in name_parcels)

def test_parcel_detail():
    # Get 50/1 details
    res_search = client.get("/api/parcels/search?q=50/1")
    parcel_id = res_search.json()[0]["id"]
    
    res = client.get(f"/api/parcels/{parcel_id}")
    assert res.status_code == 200
    data = res.json()
    assert data["gat_number"] == "50/1"
    assert data["area_hectares"] == 1.82
    assert "Patil Shankar Bapu" in data["owner_name"]

def test_dashboard_statistics():
    res = client.get("/api/dashboard/statistics")
    assert res.status_code == 200
    data = res.json()
    assert "kpis" in data
    assert data["kpis"]["total_parcels"] >= 248
    assert len(data["land_types"]) > 0
    assert len(data["area_by_taluka"]) > 0
    assert len(data["recent_surveys"]) > 0

def test_boundary_comparison():
    # Search for discrepancy parcel 48/3
    res_search = client.get("/api/parcels/search?q=48/3")
    if res_search.json():
        p_id = res_search.json()[0]["id"]
        res = client.post(f"/api/parcels/{p_id}/compare-boundary")
        assert res.status_code == 200
        data = res.json()
        assert "diff_percent" in data
        assert "recommendations" in data

def test_pdf_report_generation():
    res_search = client.get("/api/parcels/search?q=50/1")
    p_id = res_search.json()[0]["id"]
    res = client.get(f"/api/reports/parcel/{p_id}/pdf")
    assert res.status_code == 200
    assert res.headers["content-type"] == "application/pdf"
    assert len(res.content) > 1000
