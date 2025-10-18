from sqlalchemy.orm import Session
from sqlalchemy import func, String
from app.database import SessionLocal
from app.models import (
    FS1_WorkforceComposition,
    FS1_WorkforceDiversity,
    FS1_EmployeeTurnover,
    FS1_EmployeeTraining,
    FS1_WorkplaceInjuries,
    D_OrganizationalUnit,
)


class KPIProcessor:

    def get_total_workforce_by_gender(
        self, company_id, years=None, organizational_unit_ids=None, country_id=None
    ):
        with SessionLocal() as db:
            gender_query = (
                db.query(
                    FS1_WorkforceComposition.GenderID,
                    func.sum(FS1_WorkforceComposition.EmployeeCount).label(
                        "total_count"
                    ),
                )
                .join(
                    D_OrganizationalUnit,
                    FS1_WorkforceComposition.OrganizationalUnitID
                    == D_OrganizationalUnit.OrganizationalUnitID,
                )
                .filter(
                    FS1_WorkforceComposition.CompanyID == company_id,
                    D_OrganizationalUnit.is_deleted == 0,
                )
            )

            if organizational_unit_ids:
                gender_query = gender_query.filter(
                    FS1_WorkforceComposition.OrganizationalUnitID.in_(
                        organizational_unit_ids
                    )
                )
            if years:
                gender_query = gender_query.filter(
                    func.substring(
                        func.cast(FS1_WorkforceComposition.DateKey, String), 1, 4
                    ).in_([str(y) for y in years])
                )
            if country_id:
                gender_query = gender_query.filter(
                    FS1_WorkforceComposition.CountryID == country_id
                )

            gender_query = gender_query.group_by(FS1_WorkforceComposition.GenderID)
            gender_data = gender_query.all()

            gender_mapping = {
                1: "Male",
                2: "Female",
                3: "Non-binary",
                4: "Transgender",
                5: "Other",
            }
            return [
                {
                    "gender": gender_mapping.get(row.GenderID, "Unknown"),
                    "employee_count": int(row.total_count),
                }
                for row in gender_data
            ]

    def get_percentage_employees_with_disabilities(
        self, company_id, years=None, organizational_unit_ids=None, country_id=None
    ):
        with SessionLocal() as db:
            # Total Employees
            emp_query = (
                db.query(
                    func.sum(FS1_WorkforceComposition.EmployeeCount).label(
                        "total_employees"
                    )
                )
                .join(
                    D_OrganizationalUnit,
                    FS1_WorkforceComposition.OrganizationalUnitID
                    == D_OrganizationalUnit.OrganizationalUnitID,
                )
                .filter(
                    FS1_WorkforceComposition.CompanyID == company_id,
                    D_OrganizationalUnit.is_deleted == 0,
                )
            )

            if organizational_unit_ids:
                emp_query = emp_query.filter(
                    FS1_WorkforceComposition.OrganizationalUnitID.in_(
                        organizational_unit_ids
                    )
                )
            if years:
                emp_query = emp_query.filter(
                    func.substring(
                        func.cast(FS1_WorkforceComposition.DateKey, String), 1, 4
                    ).in_([str(y) for y in years])
                )
            if country_id:
                emp_query = emp_query.filter(
                    FS1_WorkforceComposition.CountryID == country_id
                )

            total_employees = int(emp_query.scalar() or 0)

            # Total Disabilities
            disability_query = (
                db.query(
                    func.sum(FS1_WorkforceDiversity.DisabilityCount).label(
                        "total_disabilities"
                    )
                )
                .join(
                    D_OrganizationalUnit,
                    FS1_WorkforceDiversity.OrganizationalUnitID
                    == D_OrganizationalUnit.OrganizationalUnitID,
                )
                .filter(
                    FS1_WorkforceDiversity.CompanyID == company_id,
                    D_OrganizationalUnit.is_deleted == 0,
                )
            )
            if organizational_unit_ids:
                disability_query = disability_query.filter(
                    FS1_WorkforceDiversity.OrganizationalUnitID.in_(
                        organizational_unit_ids
                    )
                )
            if years:
                disability_query = disability_query.filter(
                    func.substring(
                        func.cast(FS1_WorkforceDiversity.DateKey, String), 1, 4
                    ).in_([str(y) for y in years])
                )
            if country_id:
                disability_query = disability_query.filter(
                    FS1_WorkforceDiversity.CountryID == country_id
                )

            total_disabilities = int(disability_query.scalar() or 0)
            overall_percentage = (
                (total_disabilities / total_employees * 100)
                if total_employees > 0
                else 0.0
            )

            # Gender Breakdown
            gender_query = (
                db.query(
                    FS1_WorkforceComposition.GenderID,
                    func.sum(FS1_WorkforceComposition.EmployeeCount).label(
                        "total_count"
                    ),
                )
                .join(
                    D_OrganizationalUnit,
                    FS1_WorkforceComposition.OrganizationalUnitID
                    == D_OrganizationalUnit.OrganizationalUnitID,
                )
                .filter(
                    FS1_WorkforceComposition.CompanyID == company_id,
                    D_OrganizationalUnit.is_deleted == 0,
                )
            )

            if organizational_unit_ids:
                gender_query = gender_query.filter(
                    FS1_WorkforceComposition.OrganizationalUnitID.in_(
                        organizational_unit_ids
                    )
                )
            if years:
                gender_query = gender_query.filter(
                    func.substring(
                        func.cast(FS1_WorkforceComposition.DateKey, String), 1, 4
                    ).in_([str(y) for y in years])
                )
            if country_id:
                gender_query = gender_query.filter(
                    FS1_WorkforceComposition.CountryID == country_id
                )

            gender_query = gender_query.group_by(FS1_WorkforceComposition.GenderID)
            gender_data = gender_query.all()

            gender_mapping = {
                1: "Male",
                2: "Female",
                3: "Non-binary",
                4: "Transgender",
                5: "Other",
            }
            gender_breakdown = []

            allocated_disabilities = 0
            for i, row in enumerate(gender_data):
                gender_total = int(row.total_count)
                if i == len(gender_data) - 1:
                    gender_disabilities = total_disabilities - allocated_disabilities
                else:
                    gender_disabilities = (
                        int(
                            round((gender_total / total_employees) * total_disabilities)
                        )
                        if total_employees > 0
                        else 0
                    )
                    allocated_disabilities += gender_disabilities

                gender_percentage = (
                    (gender_disabilities / total_disabilities * 100)
                    if total_disabilities > 0
                    else 0.0
                )
                gender_breakdown.append(
                    {
                        "gender": gender_mapping.get(row.GenderID, "Unknown"),
                        "total_employees": gender_total,
                        "employees_with_disabilities": gender_disabilities,
                        "percentage": round(gender_percentage, 2),
                    }
                )

            return {
                "overall_percentage": round(overall_percentage, 2),
                "total_employees": total_employees,
                "total_employees_with_disabilities": total_disabilities,
                "breakdown_by_gender": gender_breakdown,
            }

    def get_employee_turnover_rate(
        self, company_id, years=None, organizational_unit_ids=None, country_id=None
    ):
        with SessionLocal() as db:
            # --- Total Employees Departed ---
            departed_query = db.query(
                func.sum(FS1_EmployeeTurnover.EmployeesDeparted).label(
                    "total_employees_departed"
                )
            )
            departed_query = departed_query.join(
                D_OrganizationalUnit,
                FS1_EmployeeTurnover.OrganizationalUnitID
                == D_OrganizationalUnit.OrganizationalUnitID,
            ).filter(
                FS1_EmployeeTurnover.CompanyID == company_id,
                D_OrganizationalUnit.is_deleted == 0,
            )
            if organizational_unit_ids:
                departed_query = departed_query.filter(
                    FS1_EmployeeTurnover.OrganizationalUnitID.in_(
                        organizational_unit_ids
                    )
                )
            if years:
                departed_query = departed_query.filter(
                    func.substring(
                        func.cast(FS1_EmployeeTurnover.DateKey, String), 1, 4
                    ).in_([str(y) for y in years])
                )
            if country_id:
                departed_query = departed_query.filter(
                    FS1_EmployeeTurnover.CountryID == country_id
                )
            total_employees_departed = departed_query.scalar() or 0
            total_employees_departed = float(total_employees_departed)

            # --- Total Employees ---
            emp_query = db.query(
                func.sum(FS1_WorkforceComposition.EmployeeCount).label(
                    "total_employees"
                )
            )
            emp_query = emp_query.join(
                D_OrganizationalUnit,
                FS1_WorkforceComposition.OrganizationalUnitID
                == D_OrganizationalUnit.OrganizationalUnitID,
            ).filter(
                FS1_WorkforceComposition.CompanyID == company_id,
                D_OrganizationalUnit.is_deleted == 0,
            )
            if organizational_unit_ids:
                emp_query = emp_query.filter(
                    FS1_WorkforceComposition.OrganizationalUnitID.in_(
                        organizational_unit_ids
                    )
                )
            if years:
                emp_query = emp_query.filter(
                    func.substring(
                        func.cast(FS1_WorkforceComposition.DateKey, String), 1, 4
                    ).in_([str(y) for y in years])
                )
            if country_id:
                emp_query = emp_query.filter(
                    FS1_WorkforceComposition.CountryID == country_id
                )
            total_employees = emp_query.scalar() or 0
            total_employees = float(total_employees)

            # --- Calculate Turnover Rate ---
            turnover_rate = (
                (total_employees_departed / total_employees * 100)
                if total_employees > 0
                else 0.0
            )

            return {
                "overall_turnover_rate": round(turnover_rate, 2),
                "total_employees": int(total_employees),
                "total_employees_departed": int(total_employees_departed),
            }

    def get_average_training_hours_per_employee(
        self, company_id, years=None, organizational_unit_ids=None, country_id=None
    ):
        with SessionLocal() as db:
            # --- Total Training Hours ---
            training_query = db.query(
                func.sum(FS1_EmployeeTraining.TotalTrainingHours).label(
                    "total_training_hours"
                )
            )
            training_query = training_query.join(
                D_OrganizationalUnit,
                FS1_EmployeeTraining.OrganizationalUnitID
                == D_OrganizationalUnit.OrganizationalUnitID,
            ).filter(
                FS1_EmployeeTraining.CompanyID == company_id,
                D_OrganizationalUnit.is_deleted == 0,
            )
            if organizational_unit_ids:
                training_query = training_query.filter(
                    FS1_EmployeeTraining.OrganizationalUnitID.in_(
                        organizational_unit_ids
                    )
                )
            if years:
                training_query = training_query.filter(
                    func.substring(
                        func.cast(FS1_EmployeeTraining.DateKey, String), 1, 4
                    ).in_([str(y) for y in years])
                )
            if country_id:
                training_query = training_query.filter(
                    FS1_EmployeeTraining.CountryID == country_id
                )
            total_training_hours = training_query.scalar() or 0.0
            total_training_hours = float(total_training_hours)

            # --- Total Employees ---
            emp_query = db.query(
                func.sum(FS1_WorkforceComposition.EmployeeCount).label(
                    "total_employees"
                )
            )
            emp_query = emp_query.join(
                D_OrganizationalUnit,
                FS1_WorkforceComposition.OrganizationalUnitID
                == D_OrganizationalUnit.OrganizationalUnitID,
            ).filter(
                FS1_WorkforceComposition.CompanyID == company_id,
                D_OrganizationalUnit.is_deleted == 0,
            )
            if organizational_unit_ids:
                emp_query = emp_query.filter(
                    FS1_WorkforceComposition.OrganizationalUnitID.in_(
                        organizational_unit_ids
                    )
                )
            if years:
                emp_query = emp_query.filter(
                    func.substring(
                        func.cast(FS1_WorkforceComposition.DateKey, String), 1, 4
                    ).in_([str(y) for y in years])
                )
            if country_id:
                emp_query = emp_query.filter(
                    FS1_WorkforceComposition.CountryID == country_id
                )
            total_employees = emp_query.scalar() or 0
            total_employees = float(total_employees)

            overall_average = (
                (total_training_hours / total_employees) if total_employees > 0 else 0.0
            )

            # --- Gender Breakdown ---
            gender_query = (
                db.query(
                    FS1_WorkforceComposition.GenderID,
                    func.sum(FS1_WorkforceComposition.EmployeeCount).label(
                        "total_count"
                    ),
                )
                .join(
                    D_OrganizationalUnit,
                    FS1_WorkforceComposition.OrganizationalUnitID
                    == D_OrganizationalUnit.OrganizationalUnitID,
                )
                .filter(
                    FS1_WorkforceComposition.CompanyID == company_id,
                    D_OrganizationalUnit.is_deleted == 0,
                )
            )
            if organizational_unit_ids:
                gender_query = gender_query.filter(
                    FS1_WorkforceComposition.OrganizationalUnitID.in_(
                        organizational_unit_ids
                    )
                )
            if years:
                gender_query = gender_query.filter(
                    func.substring(
                        func.cast(FS1_WorkforceComposition.DateKey, String), 1, 4
                    ).in_([str(y) for y in years])
                )
            if country_id:
                gender_query = gender_query.filter(
                    FS1_WorkforceComposition.CountryID == country_id
                )
            gender_query = gender_query.group_by(FS1_WorkforceComposition.GenderID)
            gender_data = gender_query.all()

            gender_mapping = {
                1: "Male",
                2: "Female",
                3: "Non-binary",
                4: "Transgender",
                5: "Other",
            }
            gender_breakdown = []
            for row in gender_data:
                gender_total = float(row.total_count)
                gender_training_hours = (
                    round((gender_total / total_employees) * total_training_hours, 2)
                    if total_employees > 0
                    else 0.0
                )
                gender_average = (
                    (gender_training_hours / gender_total) if gender_total > 0 else 0.0
                )
                gender_breakdown.append(
                    {
                        "gender": gender_mapping.get(row.GenderID, "Unknown"),
                        "total_employees": int(gender_total),
                        "total_training_hours": gender_training_hours,
                        "average_hours_per_employee": round(gender_average, 2),
                    }
                )

            return {
                "overall_average_hours": round(overall_average, 2),
                "total_employees": int(total_employees),
                "total_training_hours": total_training_hours,
                "breakdown_by_gender": gender_breakdown,
            }

    def get_workplace_injury_rate(
        self, company_id, years=None, organizational_unit_ids=None, country_id=None
    ):
        with SessionLocal() as db:
            # --- Total Employees ---
            emp_query = db.query(
                func.sum(FS1_WorkforceComposition.EmployeeCount).label(
                    "total_employees"
                )
            )
            emp_query = emp_query.join(
                D_OrganizationalUnit,
                FS1_WorkforceComposition.OrganizationalUnitID
                == D_OrganizationalUnit.OrganizationalUnitID,
            ).filter(
                FS1_WorkforceComposition.CompanyID == company_id,
                D_OrganizationalUnit.is_deleted == 0,
            )
            if organizational_unit_ids:
                emp_query = emp_query.filter(
                    FS1_WorkforceComposition.OrganizationalUnitID.in_(
                        organizational_unit_ids
                    )
                )
            if years:
                emp_query = emp_query.filter(
                    func.substring(
                        func.cast(FS1_WorkforceComposition.DateKey, String), 1, 4
                    ).in_([str(y) for y in years])
                )
            if country_id:
                emp_query = emp_query.filter(
                    FS1_WorkforceComposition.CountryID == country_id
                )
            total_employees = emp_query.scalar() or 0
            total_employees = float(total_employees)

            # --- Total Injuries ---
            injury_query = db.query(
                func.sum(FS1_WorkplaceInjuries.InjuryCount).label("total_injuries")
            )
            injury_query = injury_query.join(
                D_OrganizationalUnit,
                FS1_WorkplaceInjuries.OrganizationalUnitID
                == D_OrganizationalUnit.OrganizationalUnitID,
            ).filter(
                FS1_WorkplaceInjuries.CompanyID == company_id,
                D_OrganizationalUnit.is_deleted == 0,
            )
            if organizational_unit_ids:
                injury_query = injury_query.filter(
                    FS1_WorkplaceInjuries.OrganizationalUnitID.in_(
                        organizational_unit_ids
                    )
                )
            if years:
                injury_query = injury_query.filter(
                    func.substring(
                        func.cast(FS1_WorkplaceInjuries.DateKey, String), 1, 4
                    ).in_([str(y) for y in years])
                )
            if country_id:
                injury_query = injury_query.filter(
                    FS1_WorkplaceInjuries.CountryID == country_id
                )
            total_injuries = injury_query.scalar() or 0
            total_injuries = float(total_injuries)

            injury_rate = (
                (total_injuries / total_employees) if total_employees > 0 else 0.0
            )

            return {
                "overall_injury_rate": round(injury_rate, 4),
                "total_employees": int(total_employees),
                "total_injuries": int(total_injuries),
            }

    def get_workforce_by_gender_by_org_unit(
        self, company_id, years=None, organizational_unit_ids=None, country_id=None
    ):
        with SessionLocal() as db:
            # Get only org units present in FS1_WorkforceComposition for the given filters
            org_unit_query = db.query(
                FS1_WorkforceComposition.OrganizationalUnitID
            ).filter(FS1_WorkforceComposition.CompanyID == company_id)
            if organizational_unit_ids:
                org_unit_query = org_unit_query.filter(
                    FS1_WorkforceComposition.OrganizationalUnitID.in_(
                        organizational_unit_ids
                    )
                )
            if years:
                org_unit_query = org_unit_query.filter(
                    func.substring(
                        func.cast(FS1_WorkforceComposition.DateKey, String), 1, 4
                    ).in_([str(y) for y in years])
                )
            if country_id:
                org_unit_query = org_unit_query.filter(
                    FS1_WorkforceComposition.CountryID == country_id
                )
            org_unit_ids = {row[0] for row in org_unit_query.distinct().all()}

            # Get org unit names for those present in FS1_WorkforceComposition
            org_units = (
                db.query(D_OrganizationalUnit)
                .filter(
                    D_OrganizationalUnit.CompanyID == company_id,
                    D_OrganizationalUnit.is_deleted == 0,
                    D_OrganizationalUnit.OrganizationalUnitID.in_(org_unit_ids),
                )
                .all()
            )
            org_unit_names = {
                u.OrganizationalUnitID: u.OrganizationalUnitName for u in org_units
            }

            # Query actual data from FS1_WorkforceComposition
            workforce_query = (
                db.query(
                    FS1_WorkforceComposition.OrganizationalUnitID,
                    FS1_WorkforceComposition.GenderID,
                    func.sum(FS1_WorkforceComposition.EmployeeCount).label(
                        "employee_count"
                    ),
                )
                .join(
                    D_OrganizationalUnit,
                    FS1_WorkforceComposition.OrganizationalUnitID
                    == D_OrganizationalUnit.OrganizationalUnitID,
                )
                .filter(
                    FS1_WorkforceComposition.CompanyID == company_id,
                    D_OrganizationalUnit.is_deleted == 0,
                    FS1_WorkforceComposition.OrganizationalUnitID.in_(org_unit_ids),
                )
            )
            if years:
                workforce_query = workforce_query.filter(
                    func.substring(
                        func.cast(FS1_WorkforceComposition.DateKey, String), 1, 4
                    ).in_([str(y) for y in years])
                )
            if country_id:
                workforce_query = workforce_query.filter(
                    FS1_WorkforceComposition.CountryID == country_id
                )

            workforce_query = workforce_query.group_by(
                FS1_WorkforceComposition.OrganizationalUnitID,
                FS1_WorkforceComposition.GenderID,
            )
            results = workforce_query.all()

            gender_mapping = {
                1: "Male",
                2: "Female",
                3: "Non-binary",
                4: "Transgender",
                5: "Other",
            }

            # Organize results, ensure all org units are present
            grouped = {
                ou_id: {
                    "OrganizationalUnitID": ou_id,
                    "OrganizationalUnitName": org_unit_names.get(ou_id, ""),
                    "genders": [],
                }
                for ou_id in org_unit_names
            }

            for row in results:
                ou_id = row.OrganizationalUnitID
                grouped[ou_id]["genders"].append(
                    {
                        "gender": gender_mapping.get(row.GenderID, "Unknown"),
                        "employee_count": int(row.employee_count),
                    }
                )

            # Fill missing genders with zero counts for each org unit
            for ou in grouped.values():
                present_genders = {g["gender"] for g in ou["genders"]}
                for gid, gname in gender_mapping.items():
                    if gname not in present_genders:
                        ou["genders"].append({"gender": gname, "employee_count": 0})
                ou["genders"].sort(key=lambda x: x["gender"])

            return list(grouped.values())

    def get_employee_turnover_rate_by_org_unit(
        self, company_id, years=None, organizational_unit_ids=None, country_id=None
    ):
        with SessionLocal() as db:
            # Get only org units present in FS1_EmployeeTurnover for the given filters
            org_unit_query = db.query(FS1_EmployeeTurnover.OrganizationalUnitID).filter(
                FS1_EmployeeTurnover.CompanyID == company_id
            )
            if organizational_unit_ids:
                org_unit_query = org_unit_query.filter(
                    FS1_EmployeeTurnover.OrganizationalUnitID.in_(
                        organizational_unit_ids
                    )
                )
            if years:
                org_unit_query = org_unit_query.filter(
                    func.substring(
                        func.cast(FS1_EmployeeTurnover.DateKey, String), 1, 4
                    ).in_([str(y) for y in years])
                )
            if country_id:
                org_unit_query = org_unit_query.filter(
                    FS1_EmployeeTurnover.CountryID == country_id
                )
            org_unit_ids = {
                row[0] for row in org_unit_query.distinct().all() if row[0] is not None
            }

            # Get org unit names for those present in FS1_EmployeeTurnover
            org_units = (
                db.query(D_OrganizationalUnit)
                .filter(
                    D_OrganizationalUnit.CompanyID == company_id,
                    D_OrganizationalUnit.is_deleted == 0,
                    D_OrganizationalUnit.OrganizationalUnitID.in_(org_unit_ids),
                )
                .all()
            )
            org_unit_names = {
                u.OrganizationalUnitID: u.OrganizationalUnitName for u in org_units
            }

            # Query departed employees from FS1_EmployeeTurnover
            departed_query = (
                db.query(
                    FS1_EmployeeTurnover.OrganizationalUnitID,
                    func.sum(FS1_EmployeeTurnover.EmployeesDeparted).label(
                        "total_departed"
                    ),
                )
                .join(
                    D_OrganizationalUnit,
                    FS1_EmployeeTurnover.OrganizationalUnitID
                    == D_OrganizationalUnit.OrganizationalUnitID,
                )
                .filter(
                    FS1_EmployeeTurnover.CompanyID == company_id,
                    D_OrganizationalUnit.is_deleted == 0,
                    FS1_EmployeeTurnover.OrganizationalUnitID.in_(org_unit_ids),
                )
            )
            if years:
                departed_query = departed_query.filter(
                    func.substring(
                        func.cast(FS1_EmployeeTurnover.DateKey, String), 1, 4
                    ).in_([str(y) for y in years])
                )
            if country_id:
                departed_query = departed_query.filter(
                    FS1_EmployeeTurnover.CountryID == country_id
                )
            departed_query = departed_query.group_by(
                FS1_EmployeeTurnover.OrganizationalUnitID
            )
            departed_counts = departed_query.all()

            # Query total employees from FS1_WorkforceComposition
            workforce_query = (
                db.query(
                    FS1_WorkforceComposition.OrganizationalUnitID,
                    func.sum(FS1_WorkforceComposition.EmployeeCount).label(
                        "total_employees"
                    ),
                )
                .join(
                    D_OrganizationalUnit,
                    FS1_WorkforceComposition.OrganizationalUnitID
                    == D_OrganizationalUnit.OrganizationalUnitID,
                )
                .filter(
                    FS1_WorkforceComposition.CompanyID == company_id,
                    D_OrganizationalUnit.is_deleted == 0,
                    FS1_WorkforceComposition.OrganizationalUnitID.in_(org_unit_ids),
                )
            )
            if years:
                workforce_query = workforce_query.filter(
                    func.substring(
                        func.cast(FS1_WorkforceComposition.DateKey, String), 1, 4
                    ).in_([str(y) for y in years])
                )
            if country_id:
                workforce_query = workforce_query.filter(
                    FS1_WorkforceComposition.CountryID == country_id
                )
            workforce_query = workforce_query.group_by(
                FS1_WorkforceComposition.OrganizationalUnitID
            )
            workforce_counts = workforce_query.all()

            # Merge results, ensure all org units are present
            workforce_map = {
                row.OrganizationalUnitID: int(row.total_employees)
                for row in workforce_counts
            }
            departed_map = {
                row.OrganizationalUnitID: int(row.total_departed)
                for row in departed_counts
            }

            results = []
            for ou_id in org_unit_names:
                total_employees = workforce_map.get(ou_id, 0)
                total_departed = departed_map.get(ou_id, 0)
                turnover_rate = (
                    (total_departed / total_employees * 100)
                    if total_employees > 0
                    else 0.0
                )
                results.append(
                    {
                        "OrganizationalUnitID": ou_id,
                        "OrganizationalUnitName": org_unit_names.get(ou_id, ""),
                        "total_employees": total_employees,
                        "total_employees_departed": total_departed,
                        "turnover_rate": round(turnover_rate, 2),
                    }
                )

            return results

    def get_all_kpi_data(
        self, company_id, years=None, organizational_unit_ids=None, country_id=None
    ):
        return {
            "Total Workforce by Gender": self.get_total_workforce_by_gender(
                company_id, years, organizational_unit_ids, country_id
            ),
            "Percentage of Employees with Disabilities": self.get_percentage_employees_with_disabilities(
                company_id, years, organizational_unit_ids, country_id
            ),
            "Employee Turnover Rate": self.get_employee_turnover_rate(
                company_id, years, organizational_unit_ids, country_id
            ),
            "Average Training Hours per Employee": self.get_average_training_hours_per_employee(
                company_id, years, organizational_unit_ids, country_id
            ),
            "Workplace Injury Rate": self.get_workplace_injury_rate(
                company_id, years, organizational_unit_ids, country_id
            ),
            "Workforce by Gender by Organizational Unit": self.get_workforce_by_gender_by_org_unit(
                company_id, years, organizational_unit_ids, country_id
            ),
            "Employee Turnover Rate by Organizational Unit": self.get_employee_turnover_rate_by_org_unit(
                company_id, years, organizational_unit_ids, country_id
            ),
        }


kpi_processor = KPIProcessor()
