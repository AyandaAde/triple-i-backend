from datetime import datetime, timezone
from io import BytesIO
from fastapi import APIRouter, File, UploadFile
import pandas as pd
import sqlalchemy

from app.database import SessionLocal
from app.models import (
    FS1_Diversity,
    FS1_EmployeeTraining,
    FS1_EmployeeTurnover,
    FS1_Workforce,
    FS1_WorkforceComposition,
    FS1_WorkforceDiversity,
    FS1_WorkplaceInjuries,
)
from app.kpi_processor import kpi_processor

router = APIRouter(prefix="/upload", tags=["upload"])


def parse_datekey(datekey):
    if pd.isna(datekey):
        return datetime.now()
    if isinstance(datekey, (datetime, pd.Timestamp)):
        return datekey
    datekey_str = str(datekey)
    try:
        return datetime.strptime(datekey_str, "%Y%m%d")
    except ValueError:
        try:
            return datetime.strptime(datekey_str[:10], "%Y-%m-%d")
        except ValueError:
            try:
                return pd.to_datetime(datekey)
            except Exception:
                raise ValueError(f"Cannot parse DateKey: {datekey}")


@router.post("/")
async def upload(file: UploadFile = File(...)):
    
    if not file.filename.endswith(".xlsx"):
        return {"error": "File must be an Excel .xlsx file"}

    contents = await file.read()
    try:
        all_sheets = pd.read_excel(
            BytesIO(contents), sheet_name=None, engine="openpyxl"
        )
    except Exception as e:
        return {"error": f"Failed to read Excel file: {str(e)}"}

    MODELS = {
        "injuries": {
            "model": FS1_WorkplaceInjuries,
            "required": [
                "injuryid",
                "datekey",
                "injurycount",
                "companyid",
                "countryid",
                "organizationalunitid",
                "createdat",
                "updatedat",
            ],
        },
        "workforce": {
            "model": FS1_Workforce,
            "required": [
                "workforceid",
                "datekey",
                "workforcecount",
                "companyid",
                "countryid",
                "organizationalunitid",
                "createdat",
                "updatedat",
            ],
        },
        "diversity": {
            "model": FS1_Diversity,
            "required": [
                "DiversityID",
                "DateKey",
                "CountryID",
                "CompanyID",
                "DisabilityCount",
                "OrganizationalUnitID",
                "created_at",
                "updated_at",
            ],
        },
        "workforcediversity": {
            "model": FS1_WorkforceDiversity,
            "required": [
                "diversityid",
                "datekey",
                "countryid",
                "companyid",
                "disabilitycount",
                "organizationalunitid",
                "createdat",
                "updatedat",
            ],
        },
        "workforcecomposition": {
            "model": FS1_WorkforceComposition,
            "required": [
                "workforcecompositionid",
                "datekey",
                "genderid",
                "contracttypeid",
                "countryid",
                "employeecount",
                "companyid",
                "organizationalunitid",
                "createdat",
                "updatedat",
            ],
        },
        "employeetraining": {
            "model": FS1_EmployeeTraining,
            "required": [
                "trainingid",
                "datekey",
                "totaltraininghours",
                "companyid",
                "countryid",
                "organizationalunitid",
                "createdat",
                "updatedat",
            ],
        },
        "employeeturnover": {
            "model": FS1_EmployeeTurnover,
            "required": [
                "turnoverid",
                "datekey",
                "genderid",
                "agegroupid",
                "employeesdeparted",
                "companyid",
                "contracttypeid",
                "countryid",
                "organizationalunitid",
                "createdat",
                "updatedat",
            ],
        },
    }

    processed = []
    skipped = []

    def map_record_to_model(record, model_cls):
        mapped = {}
        for col in model_cls.__table__.columns:
            col_lower = col.name.lower()
            if col_lower in record:
                value = record[col_lower]
                if isinstance(col.type, sqlalchemy.DateTime):
                    value = parse_datekey(value)
                mapped[col.name] = value
            elif col_lower in ("createdat", "created_at"):
                mapped[col.name] = datetime.now(timezone.utc)
            elif col_lower in ("updatedat", "updated_at"):
                mapped[col.name] = datetime.now(timezone.utc)
        return mapped

    with SessionLocal() as db:
        tables_to_clear = [
            FS1_WorkplaceInjuries,
            FS1_Workforce,
            FS1_Diversity,
            FS1_WorkforceDiversity,
            FS1_WorkforceComposition,
            FS1_EmployeeTraining,
            FS1_EmployeeTurnover,
        ]

        for table in tables_to_clear:
            db.query(table).delete()
        db.commit()

        for sheet_name, df in all_sheets.items():
            print(f"Processing sheet: {sheet_name}")
            df.columns = (
                df.columns.str.strip()
                .str.replace(" ", "")
                .str.replace("_", "")
                .str.lower()
            )

            matched_model = None
            for key, info in MODELS.items():
                required = [c.lower() for c in info["required"]]
                if all(col in df.columns for col in required):
                    matched_model = info
                    break

            if not matched_model:
                print(f"No matching model found for sheet '{sheet_name}'")
                skipped.append(sheet_name)
                continue

            ModelClass = matched_model["model"]
            print(f"Matched '{sheet_name}' → {ModelClass.__name__}")

            for _, row in df.iterrows():
                record_data = {col: row.get(col) for col in matched_model["required"]}
                mapped_data = map_record_to_model(record_data, ModelClass)
                instance = ModelClass(**mapped_data)
                db.add(instance)

            db.commit()
            processed.append(sheet_name)

    if not processed:
        return {"error": "No valid sheets matched any known model."}

    first_valid_df = list(all_sheets.values())[0]
    company_id = int(first_valid_df.iloc[0].get("companyid", 1))

    year = None
    for df in all_sheets.values():
        for col in df.columns:
            if str(col).lower() in ("datekey",):
                try:
                    
                    sample = str(df.iloc[0][col])
                    if len(sample) >= 4:
                        year = int(sample[:4])
                        break
                except Exception:
                    pass
        if year:
            break

    result = kpi_processor.get_all_kpi_data(company_id=company_id)

    return {
        "message": "Excel processed successfully",
        "processed_sheets": processed,
        "skipped_sheets": skipped,
        "kpi_result": result,
    }
