from typing import Dict, List, Any

COVER_PAGE_LAYOUT: Dict[str, Any] = {
    "title": "ESRS S1 Management Report",
    "show_date": True,
    "show_confidential": True,
    "show_logo": True,
    "fields": [
        {"label": "Company Name", "key": "company_name"},
        {"label": "Reporting Year", "key": "year"},
    ],
}

KPI_SUMMARY_LAYOUT: Dict[str, Any] = {
    "title": "KPI Summary",
    "description": "Summary of headline KPIs, workforce statistics, and performance metrics.",
    "columns": ["Metric", "Value"],
}

VISUALS_LAYOUT: Dict[str, Any] = {
    "title": "KPI Visualizations",
    "chart_order": [
        "workforce_by_gender",
        "training_hours_by_gender",
        "trend_training_hours_per_employee",
        "kpi_summary",
    ],
    "display_mode": "vertical",
}

NARRATIVE_LAYOUT: Dict[str, Any] = {
    "title": "Narrative",
    "sections": [
        {"title": "Executive Summary", "key": "executive_summary"},
        {"title": "1. Workforce Composition and Diversity", "key": "workforce_composition_and_diversity"},
        {"title": "2. Working Conditions and Equal Opportunity", "key": "working_conditions_and_equal_opportunity"},
        {"title": "3. Training and Development", "key": "training_and_development"},
        {"title": "4. Turnover and Retention", "key": "turnover_and_retention"},
        {"title": "5. Health and Safety", "key": "health_and_safety"},
        {"title": "6. Outlook and Next Steps", "key": "outlook_and_next_steps"},
    ],
}

CLOSING_LAYOUT: Dict[str, Any] = {
    "title": "Closing",
    "key": "closing",
    "footer_note": "End of Report — Confidential",
}

DEFAULT_LAYOUT: Dict[str, Any] = {
    "cover_page": COVER_PAGE_LAYOUT,
    "kpi_summary": KPI_SUMMARY_LAYOUT,
    "visuals": VISUALS_LAYOUT,
    "narrative": NARRATIVE_LAYOUT,
    "closing": CLOSING_LAYOUT,
}

def get_layout(template_name: str = "default") -> Dict[str, Any]:
    if template_name.lower() in ("default", "esrs_s1"):
        return DEFAULT_LAYOUT
    raise ValueError(f"Unknown layout template: {template_name}")
