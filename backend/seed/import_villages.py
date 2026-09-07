import argparse
import re
import sys
from pathlib import Path

import pandas as pd

from app.core.database import SessionLocal
from app.models.locations import District, Taluka, Village


def normalized(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def find_column(columns, names):
    normalized_columns = {normalized(column): column for column in columns}
    for name in names:
        if normalized(name) in normalized_columns:
            return normalized_columns[normalized(name)]
    for column in columns:
        value = normalized(column)
        if any(normalized(name) in value for name in names):
            return column
    return None


def import_workbook(workbook_path, sheet_name=0):
    workbook = pd.ExcelFile(workbook_path)
    sheet = workbook.sheet_names[sheet_name] if isinstance(sheet_name, int) else sheet_name
    frame = pd.read_excel(workbook_path, sheet_name=sheet, header=1, dtype=str).fillna("")
    district_column = find_column(frame.columns, ["districtnameinenglish", "districtname", "district"])
    district_code_column = find_column(frame.columns, ["districtcode", "lgddistrictcode"])
    taluka_column = find_column(frame.columns, ["subdistrictnameinenglish", "subdistrictname", "talukaname", "taluka"])
    taluka_code_column = find_column(frame.columns, ["subdistrictcode", "talukacode", "lgdsubdistrictcode"])
    village_column = find_column(frame.columns, ["villagenameinenglish", "villagename", "village"])
    village_code_column = find_column(frame.columns, ["villagecode", "lgdvillagecode"])

    missing = [name for name, column in {
        "district": district_column,
        "sub-district/taluka": taluka_column,
        "village": village_column,
    }.items() if column is None]
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(missing)}. Found: {list(frame.columns)}")

    db = SessionLocal()
    districts = {}
    talukas = {}
    villages = 0
    try:
        for _, row in frame.iterrows():
            district_name = str(row[district_column]).strip()
            taluka_name = str(row[taluka_column]).strip()
            village_name = str(row[village_column]).strip()
            if not district_name or not taluka_name or not village_name:
                continue

            district = districts.get(district_name)
            if district is None:
                district = db.query(District).filter(District.name == district_name).first()
                if district is None:
                    district = District(name=district_name, state="Maharashtra")
                    db.add(district)
                    db.flush()
                if district_code_column:
                    district.code = str(row[district_code_column]).strip() or district.code
                districts[district_name] = district

            taluka_key = (district.id, taluka_name)
            taluka = talukas.get(taluka_key)
            if taluka is None:
                taluka = db.query(Taluka).filter(
                    Taluka.district_id == district.id, Taluka.name == taluka_name
                ).first()
                if taluka is None:
                    taluka = Taluka(name=taluka_name, district_id=district.id)
                    db.add(taluka)
                    db.flush()
                if taluka_code_column:
                    taluka.code = str(row[taluka_code_column]).strip() or taluka.code
                talukas[taluka_key] = taluka

            village = db.query(Village).filter(
                Village.taluka_id == taluka.id, Village.name == village_name
            ).first()
            if village is None:
                village = Village(
                    name=village_name,
                    taluka_id=taluka.id,
                    center_lat=0.0,
                    center_lng=0.0,
                )
                db.add(village)
            if village_code_column:
                village.code = str(row[village_code_column]).strip() or village.code
            villages += 1

        db.commit()
        print(f"Imported {len(districts)} districts, {len(talukas)} sub-districts, {villages} village rows from {workbook_path}")
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import an official LGD village workbook into LandSetu.")
    parser.add_argument("workbook", type=Path)
    parser.add_argument("--sheet", default=0, help="Excel sheet name or zero-based sheet index")
    args = parser.parse_args()
    try:
        sheet = int(args.sheet)
    except ValueError:
        sheet = args.sheet
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import_workbook(args.workbook, sheet)