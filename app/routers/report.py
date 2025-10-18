from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict, Optional

from app.templates.layouts import get_layout
from app.file_export import generate_docx_report, generate_pdf_report
from app.report_generator import generate_management_report


class ReportRequest(BaseModel):
    company_id: int
    year: int
    company_name: Optional[str] = None
    kpi_data: Dict[str, Any]
    historical_kpi_data: Optional[Dict[str, Any]] = None
    type: str = "pdf"


router = APIRouter(prefix="/report", tags=["report"])


@router.post("/")
async def create_report(payload: ReportRequest):

    openai_model = "gpt-4o-mini"
    layout = get_layout("default")

    kpi_data = payload.kpi_data
    company_id = payload.company_id
    year = payload.year
    company_name = payload.company_name
    historical_kpi_data = payload.historical_kpi_data
    type = payload.type

    result = await generate_management_report(
        kpi_data=kpi_data,
        historical_kpi_data=historical_kpi_data,
        openai_model=openai_model,
    )

    sections = result.get("sections", {})
    charts = result.get("charts", {})
    file_name = None
    file_b64 = None

    if type == "docx":
        file_name, file_b64 = generate_docx_report(
            company_id=company_id,
            year=year,
            company_name=company_name,
            kpi_data=kpi_data,
            charts=charts,
            executive_summary=sections.get("executive_summary", ""),
            workforce_composition_and_diversity=sections.get(
                "workforce_composition_and_diversity", ""
            ),
            working_conditions_and_equal_opportunity=sections.get(
                "working_conditions_and_equal_opportunity", ""
            ),
            training_and_development=sections.get("training_and_development", ""),
            turnover_and_retention=sections.get("turnover_and_retention", ""),
            health_and_safety=sections.get("health_and_safety", ""),
            outlook_and_next_steps=sections.get("outlook_and_next_steps", ""),
            closing=sections.get("closing", ""),
            layout_template=layout,
        )

    else:
        file_name, file_b64 = generate_pdf_report(
            company_id=company_id,
            year=year,
            company_name=company_name,
            kpi_data=kpi_data,
            charts=charts,
            executive_summary=sections.get("executive_summary", ""),
            workforce_composition_and_diversity=sections.get(
                "workforce_composition_and_diversity", ""
            ),
            working_conditions_and_equal_opportunity=sections.get(
                "working_conditions_and_equal_opportunity", ""
            ),
            training_and_development=sections.get("training_and_development", ""),
            turnover_and_retention=sections.get("turnover_and_retention", ""),
            health_and_safety=sections.get("health_and_safety", ""),
            outlook_and_next_steps=sections.get("outlook_and_next_steps", ""),
            closing=sections.get("closing", ""),
            layout_template=layout,
        )

    return {
        "sections": sections,
        "charts": charts,
        "file": {
            "name": file_name,
            "base64": file_b64,
        },
    }
