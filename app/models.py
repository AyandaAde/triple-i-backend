from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime
from app.database import Base


class D_OrganizationalUnit(Base):
    __tablename__ = "D_OrganizationalUnit"
    OrganizationalUnitID = Column(Integer, primary_key=True, index=True)
    OrganizationalUnitName = Column(String)
    CompanyID = Column(Integer)
    is_deleted = Column(Integer, default=0)


class FS1_WorkforceDiversity(Base):
    __tablename__ = "FS1_WorkforceDiversity"

    DiversityID = Column(Integer, primary_key=True, index=True)
    DateKey = Column(Integer, nullable=False)
    CountryID = Column(Integer, nullable=False)
    CompanyID = Column(Integer, nullable=False)
    DisabilityCount = Column(Integer, nullable=False)
    OrganizationalUnitID = Column(Integer, nullable=False)
    CreatedAt = Column(DateTime)
    UpdatedAt = Column(DateTime)


class FS1_WorkforceComposition(Base):
    __tablename__ = "FS1_WorkforceComposition"

    WorkforceCompositionID = Column(Integer, primary_key=True, index=True)
    DateKey = Column(Integer, nullable=False)
    GenderID = Column(Integer, nullable=False)
    ContractTypeID = Column(Integer, nullable=False)
    CountryID = Column(Integer, nullable=False)
    EmployeeCount = Column(Integer, nullable=False)
    CompanyID = Column(Integer, nullable=False)
    OrganizationalUnitID = Column(Integer, nullable=False)
    CreatedAt = Column(DateTime)
    UpdatedAt = Column(DateTime)


class FS1_EmployeeTraining(Base):
    __tablename__ = "FS1_EmployeeTraining"

    TrainingID = Column(Integer, primary_key=True, index=True)
    DateKey = Column(Integer, nullable=False)
    TotalTrainingHours = Column(Float, nullable=False)
    CompanyID = Column(Integer, nullable=False)
    CountryID = Column(Integer, nullable=False)
    OrganizationalUnitID = Column(Integer, nullable=False)
    CreatedAt = Column(DateTime)
    UpdatedAt = Column(DateTime)


class FS1_EmployeeTurnover(Base):
    __tablename__ = "FS1_EmployeeTurnover"

    TurnoverID = Column(Integer, primary_key=True, index=True)
    DateKey = Column(Integer, nullable=False)
    GenderID = Column(Integer, nullable=False)
    AgeGroupID = Column(Integer, nullable=False)
    EmployeesDeparted = Column(Integer, nullable=False)
    CompanyID = Column(Integer, nullable=False)
    ContractTypeID = Column(Integer, nullable=False)
    CountryID = Column(Integer, nullable=False)
    OrganizationalUnitID = Column(Integer, nullable=False)
    CreatedAt = Column(DateTime)
    UpdatedAt = Column(DateTime)


class FS1_WorkplaceInjuries(Base):
    __tablename__ = "FS1_WorkplaceInjuries"
    InjuryID = Column(Integer, primary_key=True, index=True)
    DateKey = Column(DateTime)
    InjuryCount = Column(Integer)
    CompanyID = Column(Integer)
    CountryID = Column(Integer)
    OrganizationalUnitID = Column(Integer)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=datetime.now(timezone.utc),
    )


class FS1_Workforce(Base):
    __tablename__ = "FS1_Workforce"
    WorkforceID = Column(Integer, primary_key=True, index=True)
    DateKey = Column(DateTime)
    WorkforceCount = Column(Integer)
    CompanyID = Column(Integer)
    CountryID = Column(Integer)
    OrganizationalUnitID = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)


class FS1_Diversity(Base):
    __tablename__ = "FS1_Diversity"

    DiversityID = Column(Integer, primary_key=True, index=True)
    DateKey = Column(DateTime)
    CountryID = Column(Integer)
    CompanyID = Column(Integer)
    DisabilityCount = Column(Integer)
    OrganizationalUnitID = Column(Integer)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
