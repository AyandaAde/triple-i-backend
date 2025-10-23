import asyncio
import base64
import io
import tempfile
from typing import Dict, Any, Optional
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from docx import Document
from reportlab.pdfgen import canvas
from PIL import Image

# Mock data for testing
SAMPLE_KPI_DATA = {
    "Total Workforce by Gender": [
        {"gender": "Male", "employee_count": 430},
        {"gender": "Female", "employee_count": 379},
        {"gender": "Non-binary", "employee_count": 26},
        {"gender": "Other", "employee_count": 358},
    ],
    "Percentage of Employees with Disabilities": {
        "overall_percentage": 39.56,
        "total_employees": 1193,
        "total_employees_with_disabilities": 472,
        "breakdown_by_gender": [
            {
                "gender": "Male",
                "total_employees": 430,
                "employees_with_disabilities": 170,
                "percentage": 36.02,
            },
            {
                "gender": "Female",
                "total_employees": 379,
                "employees_with_disabilities": 150,
                "percentage": 31.78,
            },
            {
                "gender": "Non-binary",
                "total_employees": 26,
                "employees_with_disabilities": 10,
                "percentage": 2.12,
            },
            {
                "gender": "Other",
                "total_employees": 358,
                "employees_with_disabilities": 142,
                "percentage": 30.08,
            },
        ],
    },
    "Employee Turnover Rate": {
        "overall_turnover_rate": 13.16,
        "total_employees": 1193,
        "total_employees_departed": 157,
    },
    "Average Training Hours per Employee": {
        "overall_average_hours": 2.67,
        "total_employees": 1193,
        "total_training_hours": 3190,
        "breakdown_by_gender": [
            {
                "gender": "Male",
                "total_employees": 430,
                "total_training_hours": 1149.79,
                "average_hours_per_employee": 2.67,
            },
            {
                "gender": "Female",
                "total_employees": 379,
                "total_training_hours": 1013.42,
                "average_hours_per_employee": 2.67,
            },
            {
                "gender": "Non-binary",
                "total_employees": 26,
                "total_training_hours": 69.52,
                "average_hours_per_employee": 2.67,
            },
            {
                "gender": "Other",
                "total_employees": 358,
                "total_training_hours": 957.27,
                "average_hours_per_employee": 2.67,
            },
        ],
    },
    "Workplace Injury Rate": {
        "overall_injury_rate": 0.0285,
        "total_employees": 1193,
        "total_injuries": 34,
    },
    "Workforce by Gender by Organizational Unit": [
        {
            "OrganizationalUnitID": 1,
            "OrganizationalUnitName": "HR",
            "genders": [
                {"gender": "Female", "employee_count": 379},
                {"gender": "Male", "employee_count": 430},
                {"gender": "Non-binary", "employee_count": 26},
                {"gender": "Other", "employee_count": 358},
                {"gender": "Transgender", "employee_count": 0},
            ],
        }
    ],
    "Employee Turnover Rate by Organizational Unit": [
        {
            "OrganizationalUnitID": 1,
            "OrganizationalUnitName": "HR",
            "total_employees": 1193,
            "total_employees_departed": 157,
            "turnover_rate": 13.16,
        }
    ],
}


SAMPLE_HISTORICAL_KPI_DATA = {
    "Average Training Hours per Employee": {
        "overall_average_hours": 20.1,
        "breakdown_by_gender": [
            {"gender": "Male", "total_training_hours": 18.5},
            {"gender": "Female", "total_training_hours": 22.0},
        ],
    },
    "Employee Turnover Rate": {
        "overall_turnover_rate": 15.2,
        "breakdown_by_gender": [
            {"gender": "Male", "turnover_rate": 14.0},
            {"gender": "Female", "turnover_rate": 16.8},
        ],
    },
}


SAMPLE_CHARTS = {
    "workforce_by_gender": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==", 
    "training_hours_by_gender": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
    "trend_training_hours_per_employee": "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg==",
}

SAMPLE_SECTIONS = {
    "executive_summary": "This is a sample executive summary for testing purposes.",
    "workforce_composition_and_diversity": "Sample workforce composition analysis with ESRS S1-1 and S1-9 references.",
    "working_conditions_and_equal_opportunity": "Sample working conditions analysis referencing S1-2 and S1-3.",
    "training_and_development": "Sample training analysis with S1-13 references.",
    "turnover_and_retention": "Sample turnover analysis aligned with ESRS S1 concepts.",
    "health_and_safety": "Sample health and safety analysis referencing S1-14.",
    "outlook_and_next_steps": "Sample outlook section with management next steps.",
    "closing": "Sample closing paragraph synthesizing insights and reaffirming commitment.",
}


@pytest.fixture
def sample_kpi_data():
    return SAMPLE_KPI_DATA.copy()


@pytest.fixture
def sample_historical_kpi_data():
    return SAMPLE_HISTORICAL_KPI_DATA.copy()


@pytest.fixture
def sample_charts():
    return SAMPLE_CHARTS.copy()


@pytest.fixture
def sample_sections():
    return SAMPLE_SECTIONS.copy()
