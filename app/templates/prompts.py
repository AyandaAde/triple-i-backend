from typing import Dict


SECTION_GUIDANCE: Dict[str, str] = {
    "executive_summary": (
        "Write a formal executive summary (max 3 sentences) that provides an overview of the "
        "company's ESRS S1 performance, highlighting key metrics and trends."
    ),
    "workforce_composition_and_diversity": (
        "Analyze workforce composition and diversity metrics (S1-1, S1-9) with gender distribution, "
        "inclusion considerations, and any material imbalances (max 3 sentences)."
    ),
    "working_conditions_and_equal_opportunity": (
        "Discuss working conditions and equal opportunity policies and outcomes, referencing S1-2 and S1-3 "
        "where applicable (max 3 sentences)."
    ),
    "training_and_development": (
        "Analyze training and development metrics, referencing S1-13 and observed trends in capability "
        "building (max 3 sentences)."
    ),
    "turnover_and_retention": (
        "Interpret turnover and retention dynamics with potential drivers, aligned with ESRS S1 concepts "
        "(max 3 sentences)."
    ),
    "health_and_safety": (
        "Summarize workplace health and safety metrics with emphasis on safe working environments, referencing "
        "S1-14 where relevant (max 3 sentences)."
    ),
    "outlook_and_next_steps": (
        "Outline management's next steps to improve performance across S1 topics with clear follow-up actions "
        "(max 5 sentences)."
    ),
    "closing": (
        "Write a concise but formal closing paragraph (max 5 sentences) that synthesizes insights, highlights "
        "progress/challenges, reaffirms commitment to continuous improvement, and maintains a confident, "
        "forward-looking tone."
    ),
}


def build_section_prompt(section_name: str, kpi_json: str, hist_json: str) -> str:
    guidance = SECTION_GUIDANCE.get(section_name, "Write a professional ESG narrative section.")
    return (
        f"You are an ESG reporting analyst. Write the '{section_name}' section for an ESRS S1 Management Report.\n\n"
        f"Requirements: {guidance}\n\n"
        f"Current KPI Data:\n{kpi_json}\n\n"
        f"Historical KPI Data (optional):\n{hist_json}\n\n"
        "Return only the section text, no JSON wrapper or additional formatting."
    )


