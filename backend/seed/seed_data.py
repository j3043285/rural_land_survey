import json
import random
from datetime import datetime, timedelta
from app.core.database import SessionLocal, Base, engine
from app.core.security import get_password_hash
from app.models.users import User, UserRole
from app.models.locations import District, Taluka, Village
from app.models.parcels import LandParcel, Farmer, ParcelOwner, CropRecord, MutationRecord, BoundaryStatus, LandType
from app.models.surveys import SurveyRecord, SurveyPoint, ParcelBoundary, SurveyStatus
from app.models.discrepancies import Discrepancy, DiscrepancyType, DiscrepancySeverity, DiscrepancyStatus
from app.models.documents import Document
from app.models.system import Notification, AuditLog

def seed():
    # Recreate tables
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    # Clear existing if any
    db.query(AuditLog).delete()
    db.query(Notification).delete()
    db.query(Document).delete()
    db.query(Discrepancy).delete()
    db.query(ParcelBoundary).delete()
    db.query(SurveyPoint).delete()
    db.query(SurveyRecord).delete()
    db.query(MutationRecord).delete()
    db.query(CropRecord).delete()
    db.query(ParcelOwner).delete()
    db.query(LandParcel).delete()
    db.query(Farmer).delete()
    db.query(Village).delete()
    db.query(Taluka).delete()
    db.query(District).delete()
    db.query(User).delete()
    db.commit()

    print("Creating default users...")
    admin = User(
        full_name="Rajendra Deshmukh (Admin)",
        email="admin@landsetu.gov.in",
        username="admin",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        phone="+91 98220 12345",
        badge_number="MH-ADM-001"
    )
    surveyor = User(
        full_name="Bhumi Abhilekh Surveyor",
        email="surveyor@landsetu.gov.in",
        username="surveyor",
        hashed_password=get_password_hash("surveyor123"),
        role=UserRole.SURVEYOR,
        phone="+91 94231 67890",
        badge_number="MH-SURV-089"
    )
    verifier = User(
        full_name="Circle Officer / Verifier",
        email="verifier@landsetu.gov.in",
        username="verifier",
        hashed_password=get_password_hash("verifier123"),
        role=UserRole.VERIFIER,
        phone="+91 98810 54321",
        badge_number="MH-VERIF-042"
    )
    viewer = User(
        full_name="Public Citizen Viewer",
        email="viewer@landsetu.gov.in",
        username="viewer",
        hashed_password=get_password_hash("viewer123"),
        role=UserRole.VIEWER,
        phone="+91 97654 11223",
        badge_number="MH-PUB-101"
    )
    db.add_all([admin, surveyor, verifier, viewer])
    db.commit()

    print("Creating Maharashtra Districts, Talukas & Villages...")
    nashik_dist = District(name="Nashik", state="Maharashtra", code="MH-NSK", center_lat=19.9975, center_lng=73.7898)
    db.add(nashik_dist)
    db.commit()

    yeola_taluka = Taluka(name="Yeola", code="YLA", district_id=nashik_dist.id, center_lat=19.1234, center_lng=74.4321)
    nashik_taluka = Taluka(name="Nashik", code="NSK", district_id=nashik_dist.id, center_lat=19.9975, center_lng=73.7898)
    sinnar_taluka = Taluka(name="Sinnar", code="SNR", district_id=nashik_dist.id, center_lat=19.8456, center_lng=74.0012)
    dindori_taluka = Taluka(name="Dindori", code="DND", district_id=nashik_dist.id, center_lat=20.2014, center_lng=73.8345)
    kalwan_taluka = Taluka(name="Kalwan", code="KLW", district_id=nashik_dist.id, center_lat=20.4901, center_lng=73.9876)
    db.add_all([yeola_taluka, nashik_taluka, sinnar_taluka, dindori_taluka, kalwan_taluka])
    db.commit()

    # Villages in Yeola
    pimpalgaon = Village(
        name="Pimpalgaon",
        code="PMP-01",
        taluka_id=yeola_taluka.id,
        center_lat=19.1234,
        center_lng=74.4321,
        boundary_geojson=json.dumps({
            "type": "Polygon",
            "coordinates": [[
                [74.4250, 19.1180],
                [74.4410, 19.1190],
                [74.4430, 19.1300],
                [74.4360, 19.1350],
                [74.4270, 19.1320],
                [74.4230, 19.1240],
                [74.4250, 19.1180]
            ]]
        })
    )
    savargaon = Village(name="Savargaon", code="SVG-02", taluka_id=yeola_taluka.id, center_lat=19.1450, center_lng=74.4120)
    andarsul = Village(name="Andarsul", code="ADL-03", taluka_id=yeola_taluka.id, center_lat=19.1020, center_lng=74.4670)
    db.add_all([pimpalgaon, savargaon, andarsul])
    db.commit()

    print("Creating Farmers and Parcels matching the exact dashboard UI...")

    # Key Cadastral Parcels with exact polygon positions matching screenshot layout
    # Center is near 19.1234, 74.4321
    # 50/1 is in the center, 48/3 is red discrepancy on top-right, 48/1 & 48/2 top, etc.
    parcels_data = [
        {
            "survey": "50/1", "gat": "50/1", "khata": "1042",
            "owner": "Patil Shankar Bapu", "mobile": "+91 98221 44556",
            "area_ha": 1.82, "area_ac": 4.50,
            "type": LandType.AGRICULTURAL_KHARIF.value,
            "status": BoundaryStatus.VERIFIED, "discrepancy": "No Discrepancy",
            "remarks": "Boundary matched with GPS",
            "lat": 19.1234, "lng": 74.4321,
            "poly": [
                [74.4305, 19.1215],
                [74.4338, 19.1228],
                [74.4322, 19.1252],
                [74.4290, 19.1238],
                [74.4305, 19.1215]
            ],
            "old_poly": [
                [74.4305, 19.1215],
                [74.4338, 19.1228],
                [74.4322, 19.1252],
                [74.4290, 19.1238],
                [74.4305, 19.1215]
            ],
            "date": datetime(2025, 4, 12, 14, 30)
        },
        {
            "survey": "48/3", "gat": "48/3", "khata": "1018",
            "owner": "Kulkarni Suresh Ramesh", "mobile": "+91 98501 22334",
            "area_ha": 2.15, "area_ac": 5.31,
            "type": LandType.AGRICULTURAL_KHARIF.value,
            "status": BoundaryStatus.DISCREPANCY, "discrepancy": "Boundary Mismatch (+7.5%)",
            "remarks": "Encroachment detected on eastern bund with Gat 50/2",
            "lat": 19.1275, "lng": 74.4345,
            "poly": [
                [74.4318, 19.1265],
                [74.4362, 19.1278],
                [74.4348, 19.1305],
                [74.4310, 19.1285],
                [74.4318, 19.1265]
            ],
            "old_poly": [
                [74.4318, 19.1265],
                [74.4348, 19.1272],
                [74.4338, 19.1298],
                [74.4310, 19.1285],
                [74.4318, 19.1265]
            ],
            "date": datetime(2025, 4, 11, 11, 15)
        },
        {
            "survey": "48/1", "gat": "48/1", "khata": "1012",
            "owner": "Jadhav Prakash Ganpat", "mobile": "+91 94220 88990",
            "area_ha": 1.95, "area_ac": 4.82,
            "type": LandType.AGRICULTURAL_KHARIF.value,
            "status": BoundaryStatus.VERIFIED, "discrepancy": "No Discrepancy",
            "remarks": "Boundary markers verified with adjacent farmers",
            "lat": 19.1288, "lng": 74.4300,
            "poly": [
                [74.4285, 19.1270],
                [74.4315, 19.1282],
                [74.4308, 19.1315],
                [74.4278, 19.1300],
                [74.4285, 19.1270]
            ],
            "old_poly": None,
            "date": datetime(2025, 4, 10, 16, 20)
        },
        {
            "survey": "48/2", "gat": "48/2", "khata": "1015",
            "owner": "Shinde Ashok Vitthal", "mobile": "+91 97300 44332",
            "area_ha": 2.40, "area_ac": 5.93,
            "type": LandType.HORTICULTURE.value,
            "status": BoundaryStatus.VERIFIED, "discrepancy": "No Discrepancy",
            "remarks": "Pomegranate orchard with drip irrigation",
            "lat": 19.1275, "lng": 74.4265,
            "poly": [
                [74.4248, 19.1255],
                [74.4282, 19.1268],
                [74.4275, 19.1298],
                [74.4240, 19.1285],
                [74.4248, 19.1255]
            ],
            "old_poly": None,
            "date": datetime(2025, 4, 9, 10, 45)
        },
        {
            "survey": "49/1", "gat": "49/1", "khata": "1022",
            "owner": "Deshmukh Sanjay Baban", "mobile": "+91 98900 11223",
            "area_ha": 2.80, "area_ac": 6.92,
            "type": LandType.AGRICULTURAL_KHARIF.value,
            "status": BoundaryStatus.VERIFIED, "discrepancy": "No Discrepancy",
            "remarks": "Soybean and Onion multi-crop field",
            "lat": 19.1245, "lng": 74.4260,
            "poly": [
                [74.4252, 19.1228],
                [74.4288, 19.1240],
                [74.4280, 19.1265],
                [74.4245, 19.1252],
                [74.4252, 19.1228]
            ],
            "old_poly": None,
            "date": datetime(2025, 4, 8, 15, 10)
        },
        {
            "survey": "49/2", "gat": "49/2", "khata": "1030",
            "owner": "Gaikwad Ramesh Tukaram", "mobile": "+91 94234 55667",
            "area_ha": 1.70, "area_ac": 4.20,
            "type": LandType.AGRICULTURAL_KHARIF.value,
            "status": BoundaryStatus.VERIFIED, "discrepancy": "No Discrepancy",
            "remarks": "GPS matched with survey stones",
            "lat": 19.1255, "lng": 74.4298,
            "poly": [
                [74.4289, 19.1242],
                [74.4318, 19.1252],
                [74.4310, 19.1278],
                [74.4282, 19.1266],
                [74.4289, 19.1242]
            ],
            "old_poly": None,
            "date": datetime(2025, 4, 7, 12, 0)
        },
        {
            "survey": "50/2", "gat": "50/2", "khata": "1045",
            "owner": "Patil Dnyaneshwar Bapu", "mobile": "+91 98224 66778",
            "area_ha": 2.10, "area_ac": 5.19,
            "type": LandType.AGRICULTURAL_KHARIF.value,
            "status": BoundaryStatus.VERIFIED, "discrepancy": "No Discrepancy",
            "remarks": "Neighboring 50/1, shared irrigation well",
            "lat": 19.1248, "lng": 74.4358,
            "poly": [
                [74.4340, 19.1230],
                [74.4378, 19.1245],
                [74.4362, 19.1275],
                [74.4325, 19.1258],
                [74.4340, 19.1230]
            ],
            "old_poly": None,
            "date": datetime(2025, 4, 6, 14, 0)
        },
        {
            "survey": "51/1", "gat": "51/1", "khata": "1050",
            "owner": "Pawar Nitin Pandurang", "mobile": "+91 94210 99887",
            "area_ha": 2.76, "area_ac": 6.82,
            "type": LandType.AGRICULTURAL_KHARIF.value,
            "status": BoundaryStatus.VERIFIED, "discrepancy": "No Discrepancy",
            "remarks": "Ground boundary pillars intact",
            "lat": 19.1210, "lng": 74.4350,
            "poly": [
                [74.4335, 19.1195],
                [74.4372, 19.1210],
                [74.4358, 19.1235],
                [74.4320, 19.1220],
                [74.4335, 19.1195]
            ],
            "old_poly": None,
            "date": datetime(2025, 4, 9, 16, 45)
        },
        {
            "survey": "52/1", "gat": "52/1", "khata": "1058",
            "owner": "Bhosale Ananda Marutirao", "mobile": "+91 98811 77665",
            "area_ha": 1.95, "area_ac": 4.82,
            "type": LandType.AGRICULTURAL_KHARIF.value,
            "status": BoundaryStatus.VERIFIED, "discrepancy": "No Discrepancy",
            "remarks": "Bordering village stream buffer",
            "lat": 19.1220, "lng": 74.4385,
            "poly": [
                [74.4370, 19.1205],
                [74.4405, 19.1220],
                [74.4392, 19.1248],
                [74.4358, 19.1232],
                [74.4370, 19.1205]
            ],
            "old_poly": None,
            "date": datetime(2025, 4, 8, 9, 30)
        },
        {
            "survey": "52/2", "gat": "52/2", "khata": "1062",
            "owner": "More Kailas Dagdu", "mobile": "+91 97633 22110",
            "area_ha": 3.10, "area_ac": 7.66,
            "type": LandType.AGRICULTURAL_KHARIF.value,
            "status": BoundaryStatus.VERIFIED, "discrepancy": "No Discrepancy",
            "remarks": "Double cropped wheat and gram",
            "lat": 19.1240, "lng": 74.4405,
            "poly": [
                [74.4390, 19.1225],
                [74.4428, 19.1240],
                [74.4412, 19.1272],
                [74.4375, 19.1255],
                [74.4390, 19.1225]
            ],
            "old_poly": None,
            "date": datetime(2025, 4, 5, 11, 0)
        },
        {
            "survey": "53/1", "gat": "53/1", "khata": "1070",
            "owner": "Wagh Vinayak Ramdas", "mobile": "+91 94225 33445",
            "area_ha": 2.25, "area_ac": 5.56,
            "type": LandType.AGRICULTURAL_KHARIF.value,
            "status": BoundaryStatus.VERIFIED, "discrepancy": "No Discrepancy",
            "remarks": "Southern farm road frontage verified",
            "lat": 19.1205, "lng": 74.4285,
            "poly": [
                [74.4265, 19.1190],
                [74.4302, 19.1205],
                [74.4290, 19.1230],
                [74.4255, 19.1215],
                [74.4265, 19.1190]
            ],
            "old_poly": None,
            "date": datetime(2025, 4, 4, 15, 30)
        },
        {
            "survey": "53/2", "gat": "53/2", "khata": "1074",
            "owner": "Ahire Santosh Bhika", "mobile": "+91 98509 88776",
            "area_ha": 3.12, "area_ac": 7.71,
            "type": LandType.AGRICULTURAL_KHARIF.value,
            "status": BoundaryStatus.IN_PROGRESS, "discrepancy": "Under Inspection",
            "remarks": "Field boundary markers pending at NW corner",
            "lat": 19.1190, "lng": 74.4315,
            "poly": [
                [74.4298, 19.1175],
                [74.4338, 19.1190],
                [74.4325, 19.1218],
                [74.4288, 19.1202],
                [74.4298, 19.1175]
            ],
            "old_poly": None,
            "date": datetime(2025, 4, 10, 14, 0)
        },
        {
            "survey": "59/1", "gat": "59/1", "khata": "1085",
            "owner": "Sonawane Dilip Dashrath", "mobile": "+91 97660 55443",
            "area_ha": 2.50, "area_ac": 6.18,
            "type": LandType.HORTICULTURE.value,
            "status": BoundaryStatus.VERIFIED, "discrepancy": "No Discrepancy",
            "remarks": "Grape vineyard with wire trellis",
            "lat": 19.1235, "lng": 74.4230,
            "poly": [
                [74.4215, 19.1220],
                [74.4250, 19.1232],
                [74.4242, 19.1258],
                [74.4208, 19.1245],
                [74.4215, 19.1220]
            ],
            "old_poly": None,
            "date": datetime(2025, 4, 3, 11, 15)
        }
    ]

    # Generate additional parcels to reach 50+ total registered records in database
    first_names = ["Shankar", "Suresh", "Prakash", "Ashok", "Sanjay", "Ramesh", "Dnyaneshwar", "Nitin", "Ananda", "Kailas", "Vinayak", "Santosh", "Dilip", "Bapu", "Balasaheb", "Chandrakant", "Govind", "Pandurang", "Machhindra", "Namdeo"]
    last_names = ["Patil", "Deshmukh", "Kulkarni", "Jadhav", "Shinde", "Gaikwad", "Pawar", "Bhosale", "More", "Wagh", "Ahire", "Sonawane", "Khairnar", "Gite", "Barde", "Darade", "Tribhuvan", "Borade"]
    land_types_pool = [
        LandType.AGRICULTURAL_KHARIF.value,
        LandType.AGRICULTURAL_RABI.value,
        LandType.HORTICULTURE.value,
        LandType.FOREST.value,
        LandType.BARREN.value,
        LandType.OTHER.value
    ]

    all_parcel_objs = []
    
    for item in parcels_data:
        # Create farmer
        farmer = Farmer(
            full_name=item["owner"],
            aadhaar_masked=f"XXXX-XXXX-{random.randint(1000, 9999)}",
            mobile=item["mobile"],
            address=f"At Post Pimpalgaon, Taluka Yeola, Dist Nashik",
            village_id=pimpalgaon.id
        )
        db.add(farmer)
        db.flush()

        # Create Land Parcel
        geojson_str = json.dumps({
            "type": "Polygon",
            "coordinates": [item["poly"]]
        })
        old_geojson_str = json.dumps({
            "type": "Polygon",
            "coordinates": [item["old_poly"]]
        }) if item.get("old_poly") else geojson_str

        parcel = LandParcel(
            survey_number=item["survey"],
            gat_number=item["gat"],
            khata_number=item["khata"],
            village_id=pimpalgaon.id,
            area_hectares=item["area_ha"],
            area_acres=item["area_ac"],
            land_type=item["type"],
            boundary_status=item["status"],
            discrepancy_status=item["discrepancy"],
            center_lat=item["lat"],
            center_lng=item["lng"],
            boundary_geojson=geojson_str,
            old_boundary_geojson=old_geojson_str,
            remarks=item["remarks"],
            last_survey_date=item["date"]
        )
        db.add(parcel)
        db.flush()

        # Link Owner
        owner_rel = ParcelOwner(parcel_id=parcel.id, farmer_id=farmer.id, ownership_share=1.0, is_primary=1)
        db.add(owner_rel)

        # Crop records
        crop = CropRecord(
            parcel_id=parcel.id,
            season="Kharif",
            year=2024,
            crop_name="Soybean / Bajra" if "Agricultural" in item["type"] else "Onions / Grapes",
            area_covered=item["area_ha"],
            irrigation_source="Well / Canal"
        )
        db.add(crop)

        # Mutation records (Ferfar)
        mutation = MutationRecord(
            parcel_id=parcel.id,
            ferfar_number=f"F-{random.randint(400, 890)}",
            mutation_date=item["date"] - timedelta(days=120),
            mutation_type="Inheritance (वारस नोंद)",
            details="Registered legal heir record updated under Section 149 of MLR Code 1966.",
            approved_by="Talathi & Circle Inspector",
            status="Certified"
        )
        db.add(mutation)

        # Survey record
        survey_rec = SurveyRecord(
            survey_number=f"SURV-2025-{item['survey'].replace('/', '-')}",
            parcel_id=parcel.id,
            surveyor_id=surveyor.id,
            verified_by_id=verifier.id if item["status"] == BoundaryStatus.VERIFIED else None,
            status=SurveyStatus.VERIFIED if item["status"] == BoundaryStatus.VERIFIED else (SurveyStatus.UNDER_REVIEW if item["status"] == BoundaryStatus.DISCREPANCY else SurveyStatus.IN_PROGRESS),
            survey_date=item["date"],
            submission_date=item["date"],
            verification_date=item["date"] if item["status"] == BoundaryStatus.VERIFIED else None,
            old_area_hectares=item["area_ha"] if item["status"] != BoundaryStatus.DISCREPANCY else 2.00,
            new_area_hectares=item["area_ha"],
            area_diff_hectares=0.0 if item["status"] != BoundaryStatus.DISCREPANCY else 0.15,
            area_diff_percent=0.0 if item["status"] != BoundaryStatus.DISCREPANCY else 7.5,
            gps_accuracy_meters=0.45,
            surveyor_remarks=item["remarks"],
            verification_remarks="Verified by Circle Officer on ground inspection" if item["status"] == BoundaryStatus.VERIFIED else "Discrepancy flagged: joint hearing scheduled"
        )
        db.add(survey_rec)
        db.flush()

        # Add survey boundary points
        for idx, pt in enumerate(item["poly"][:-1]):
            sp = SurveyPoint(
                survey_id=survey_rec.id,
                point_order=idx + 1,
                latitude=pt[1],
                longitude=pt[0],
                elevation=512.0 + idx * 0.5,
                accuracy=0.45,
                point_type="Boundary Corner Pillar",
                remarks=f"Marker stone #{idx+1}"
            )
            db.add(sp)

        # Discrepancy if 48/3
        if item["survey"] == "48/3":
            diff_poly = [
                [74.4348, 19.1272],
                [74.4362, 19.1278],
                [74.4348, 19.1305],
                [74.4338, 19.1298],
                [74.4348, 19.1272]
            ]
            disc = Discrepancy(
                parcel_id=parcel.id,
                survey_id=survey_rec.id,
                discrepancy_type=DiscrepancyType.BOUNDARY_MISMATCH,
                severity=DiscrepancySeverity.HIGH,
                status=DiscrepancyStatus.OPEN,
                old_geometry_geojson=old_geojson_str,
                new_geometry_geojson=geojson_str,
                difference_geometry_geojson=json.dumps({"type": "Polygon", "coordinates": [diff_poly]}),
                old_area_ha=2.00,
                new_area_ha=2.15,
                diff_area_ha=0.15,
                diff_percent=7.5,
                assigned_officer="Tahsildar Yeola",
                detected_date=datetime(2025, 4, 11),
                resolution_notes="Notice issued under Section 135 to neighboring plot holder."
            )
            db.add(disc)

        # Attach sample document
        doc = Document(
            title=f"7/12 Extract - Gat {item['gat']}",
            document_type="7/12 Extract",
            file_path=f"uploads/7_12_Gat_{item['gat'].replace('/', '_')}.pdf",
            file_name=f"7_12_Gat_{item['gat'].replace('/', '_')}.pdf",
            file_size_kb=420,
            mime_type="application/pdf",
            parcel_id=parcel.id,
            survey_id=survey_rec.id,
            farmer_id=farmer.id,
            uploaded_by="Surveyor",
            is_verified=True,
            ocr_extracted_text=f"Maharashtra Land Revenue Record Form VII-XII: Gat {item['gat']}, Khata {item['khata']}, Area {item['area_ha']} ha, Khatadar {item['owner']}.",
            ocr_parsed_data=json.dumps({"gat": item['gat'], "owner": item['owner'], "area": item['area_ha']})
        )
        db.add(doc)

        all_parcel_objs.append(parcel)

    # Now add 40 more peripheral parcels across Pimpalgaon, Savargaon, Andarsul to populate full village stats
    print("Generating additional parcels for comprehensive rural dataset...")
    for i in range(14, 60):
        fname = f"{random.choice(first_names)} {random.choice(first_names)} {random.choice(last_names)}"
        village_target = pimpalgaon if i < 45 else (savargaon if i < 52 else andarsul)
        
        farmer = Farmer(
            full_name=fname,
            aadhaar_masked=f"XXXX-XXXX-{random.randint(1000, 9999)}",
            mobile=f"+91 9{random.randint(100000000, 999999999)}",
            address=f"At Post {village_target.name}, Taluka Yeola, Dist Nashik",
            village_id=village_target.id
        )
        db.add(farmer)
        db.flush()

        gat_num = f"{i}/{random.choice([1, 2, 3])}"
        area_ha = round(random.uniform(0.8, 3.8), 2)
        area_ac = round(area_ha * 2.471, 2)
        
        # Spread coordinates within village bounds
        lat_offset = random.uniform(-0.012, 0.012)
        lng_offset = random.uniform(-0.014, 0.014)
        c_lat = round(village_target.center_lat + lat_offset, 5)
        c_lng = round(village_target.center_lng + lng_offset, 5)

        # Polygon around center
        dlat = random.uniform(0.0010, 0.0018)
        dlng = random.uniform(0.0010, 0.0022)
        poly = [
            [c_lng - dlng, c_lat - dlat],
            [c_lng + dlng, c_lat - dlat],
            [c_lng + dlng * 0.8, c_lat + dlat],
            [c_lng - dlng * 0.9, c_lat + dlat],
            [c_lng - dlng, c_lat - dlat]
        ]

        status_choice = random.choices(
            [BoundaryStatus.VERIFIED, BoundaryStatus.IN_PROGRESS, BoundaryStatus.DISCREPANCY, BoundaryStatus.PENDING],
            weights=[60, 20, 10, 10]
        )[0]

        has_disc = (status_choice == BoundaryStatus.DISCREPANCY)
        disc_text = "Boundary Mismatch" if has_disc else "No Discrepancy"

        poly_json = json.dumps({"type": "Polygon", "coordinates": [poly]})

        p = LandParcel(
            survey_number=gat_num,
            gat_number=gat_num,
            khata_number=str(1100 + i),
            village_id=village_target.id,
            area_hectares=area_ha,
            area_acres=area_ac,
            land_type=random.choice(land_types_pool),
            boundary_status=status_choice,
            discrepancy_status=disc_text,
            center_lat=c_lat,
            center_lng=c_lng,
            boundary_geojson=poly_json,
            old_boundary_geojson=poly_json,
            remarks="GPS surveyed with DGPS receiver",
            last_survey_date=datetime(2025, 4, random.randint(1, 12))
        )
        db.add(p)
        db.flush()

        db.add(ParcelOwner(parcel_id=p.id, farmer_id=farmer.id, ownership_share=1.0, is_primary=1))
        
        # Add survey record
        db.add(SurveyRecord(
            survey_number=f"SURV-2025-{gat_num.replace('/', '-')}",
            parcel_id=p.id,
            surveyor_id=surveyor.id,
            verified_by_id=verifier.id if status_choice == BoundaryStatus.VERIFIED else None,
            status=SurveyStatus.VERIFIED if status_choice == BoundaryStatus.VERIFIED else SurveyStatus.IN_PROGRESS,
            survey_date=datetime(2025, 4, random.randint(1, 12)),
            submission_date=datetime(2025, 4, random.randint(1, 12)),
            old_area_hectares=area_ha,
            new_area_hectares=area_ha,
            area_diff_hectares=0.0,
            area_diff_percent=0.0,
            gps_accuracy_meters=0.48,
            surveyor_remarks="Standard cadastral survey completed."
        ))

    # Add initial notifications
    db.add(Notification(
        title="Boundary Discrepancy Detected",
        message="Gat 48/3 in Pimpalgaon exceeds boundary threshold (+7.5% area mismatch with Gat 50/2).",
        notification_type="WARNING",
        is_read=False,
        link="/resurvey"
    ))
    db.add(Notification(
        title="Field Survey Verified",
        message="Survey for Gat 50/1 (Patil Shankar Bapu) has been verified by Circle Officer.",
        notification_type="SUCCESS",
        is_read=True,
        link="/parcel-records"
    ))
    db.add(Notification(
        title="GPS Network Connected",
        message="DGPS Base Station Yeola RTK Link established. Accuracy: ± 0.45m.",
        notification_type="INFO",
        is_read=True
    ))

    # Audit log
    db.add(AuditLog(
        user_id=surveyor.id,
        action="UPDATED_PARCEL_BOUNDARY",
        entity_name="LandParcel",
        entity_id="50/1",
        old_value="1.75 ha (Historical 7/12)",
        new_value="1.82 ha (DGPS Field Resurvey)",
        ip_address="19.1234, 74.4321 (Field Device)"
    ))
    db.add(AuditLog(
        user_id=verifier.id,
        action="VERIFIED_SURVEY",
        entity_name="SurveyRecord",
        entity_id="SURV-2025-50-1",
        old_value="Under Review",
        new_value="Verified & Certified",
        ip_address="127.0.0.1"
    ))

    db.commit()
    db.close()
    print("Seeding completed successfully!")

if __name__ == "__main__":
    seed()
