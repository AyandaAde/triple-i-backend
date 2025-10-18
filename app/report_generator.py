from __future__ import annotations

import asyncio
import base64
import io
import os
from typing import Any, Dict, List, Optional
from dotenv import load_dotenv
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from openai import AsyncOpenAI

load_dotenv()


def _fig_to_base64_png(fig) -> str:
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight", dpi=200)
    plt.close(fig)
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


def _plot_workforce_by_gender_pie(workforce_by_gender: List[Dict[str, Any]]) -> str:
    labels = [item.get("gender", "Unknown") for item in workforce_by_gender]
    sizes = [item.get("employee_count", 0) for item in workforce_by_gender]

    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts = ax.pie(sizes, wedgeprops=dict(width=0.4), startangle=140)
    ax.legend(
        wedges, labels, title="Gender", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1)
    )
    ax.set_title("Workforce by Gender (Donut)")

    centre_circle = plt.Circle((0, 0), 0.70, fc="white")
    fig.gca().add_artist(centre_circle)
    return _fig_to_base64_png(fig)


def _plot_training_hours_by_gender_bar(training_breakdown: List[Dict[str, Any]]) -> str:
    labels = [item.get("gender", "Unknown") for item in training_breakdown]
    values = [
        float(item.get("total_training_hours", 0.0)) for item in training_breakdown
    ]

    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(labels, values, color="#4C78A8")
    ax.set_title("Total Training Hours by Gender")
    ax.set_xlabel("Gender")
    ax.set_ylabel("Total Training Hours")
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    return _fig_to_base64_png(fig)


def _plot_trend_bar(
    title: str, current_value: float, prior_value: Optional[float]
) -> Optional[str]:
    if prior_value is None:
        return None
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["Prior"], [prior_value], color="#A0A0A0")
    ax.bar(["Current"], [current_value], color="#59A14F")
    ax.set_title(title)
    ax.set_ylabel("Value")
    ax.grid(axis="y", linestyle=":", alpha=0.5)
    return _fig_to_base64_png(fig)


def _build_section_prompt(
    section_name: str,
    kpi_data: Dict[str, Any],
    historical_kpi_data: Optional[Dict[str, Any]],
) -> str:

    def safe(obj):
        try:
            import json

            return json.dumps(obj, ensure_ascii=False)
        except Exception:
            return str(obj)

    section_guidance = {
        "executive_summary": "Write a formal executive summary (max 5 sentences) that provides an overview of the company's ESRS S1 performance, highlighting key metrics and trends.",
        "workforce_composition_and_diversity": "Analyze workforce composition and diversity metrics (S1-1, S1-9) with gender distribution, inclusion considerations, and any material imbalances (max 5 sentences).",
        "working_conditions_and_equal_opportunity": "Discuss working conditions and equal opportunity policies and outcomes, referencing S1-2 and S1-3 where applicable (max 5 sentences).",
        "training_and_development": "Analyze training and development metrics, referencing S1-13 and observed trends in capability building (max 5 sentences).",
        "turnover_and_retention": "Interpret turnover and retention dynamics with potential drivers, aligned with ESRS S1 concepts (max 5 sentences).",
        "health_and_safety": "Summarize workplace health and safety metrics with emphasis on safe working environments, referencing S1-14 where relevant (max 5 sentences).",
        "outlook_and_next_steps": "Outline management's next steps to improve performance across S1 topics with clear follow-up actions (max 5 sentences).",
        "closing": "Write a concise but formal closing paragraph (max 5 sentences) that synthesizes insights, highlights progress/challenges, reaffirms commitment to continuous improvement, and maintains a confident, forward-looking tone.",
    }

    return (
        f"You are an ESG reporting analyst. Write the '{section_name}' section for an ESRS S1 Management Report.\n\n"
        f"Requirements: {section_guidance.get(section_name, 'Write a professional ESG narrative section.')}\n\n"
        f"Current KPI Data:\n{safe(kpi_data)}\n\n"
        f"Historical KPI Data (optional):\n{safe(historical_kpi_data or {})}\n\n"
        "Return only the section text, no JSON wrapper or additional formatting."
    )


async def _generate_section_async(
    client: AsyncOpenAI,
    section_name: str,
    kpi_data: Dict[str, Any],
    historical_kpi_data: Optional[Dict[str, Any]],
    openai_model: str,
) -> str:
    try:
        prompt = _build_section_prompt(section_name, kpi_data, historical_kpi_data)
        completion = await client.chat.completions.create(
            model=openai_model,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert ESG (ESRS S1) reporting analyst.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_completion_tokens=2000,
        )
        return completion.choices[0].message.content if completion.choices else ""
    except Exception:
        return ""


async def generate_management_report(
    kpi_data: Dict[str, Any],
    *,
    historical_kpi_data: Optional[Dict[str, Any]] = None,
    openai_model: str = "gpt-4o-mini",
) -> Dict[str, Any]:

    # Build visuals from KPI data
    charts: Dict[str, Optional[str]] = {
        "workforce_by_gender": None,
        "training_hours_by_gender": None,
        "trend_training_hours_per_employee": None,
    }

    # Workforce by Gender (pie/donut)
    workforce_by_gender = kpi_data.get("Total Workforce by Gender")
    if isinstance(workforce_by_gender, list) and workforce_by_gender:
        charts["workforce_by_gender"] = _plot_workforce_by_gender_pie(
            workforce_by_gender
        )

    # Total Training Hours by Gender (bar)
    avg_training = kpi_data.get("Average Training Hours per Employee", {}) or {}
    gender_breakdown = avg_training.get("breakdown_by_gender")
    if isinstance(gender_breakdown, list) and gender_breakdown:
        charts["training_hours_by_gender"] = _plot_training_hours_by_gender_bar(
            gender_breakdown
        )

    # Trend: Training hours per employee
    current_avg = None
    prior_avg = None
    if isinstance(avg_training, dict):
        current_avg = avg_training.get("overall_average_hours")
    if historical_kpi_data and isinstance(historical_kpi_data, dict):
        hist_training = (
            historical_kpi_data.get("Average Training Hours per Employee", {}) or {}
        )
        if isinstance(hist_training, dict):
            prior_avg = hist_training.get("overall_average_hours")
    charts["trend_training_hours_per_employee"] = _plot_trend_bar(
        "Average Training Hours per Employee – YoY",
        float(current_avg) if current_avg is not None else 0.0,
        prior_avg if prior_avg is not None else None,
    )

    # Build narrative.
    async def _generate_all_sections():
        client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        sections = [
            "executive_summary",
            "workforce_composition_and_diversity",
            "working_conditions_and_equal_opportunity",
            "training_and_development",
            "turnover_and_retention",
            "health_and_safety",
            "outlook_and_next_steps",
            "closing",
        ]

        tasks = [
            _generate_section_async(
                client, section, kpi_data, historical_kpi_data, openai_model
            )
            for section in sections
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        section_results = {}
        for i, section in enumerate(sections):
            result = results[i]
            if isinstance(result, Exception) or not result:
                section_results[section] = (
                    f"Analysis for {section.replace('_', ' ').title()} section based on available KPI data."
                )
            else:
                section_results[section] = result

        return section_results

    section_results = (
        await _generate_all_sections()
        if asyncio.get_event_loop().is_running()
        else asyncio.run(_generate_all_sections())
    )

    executive_summary = section_results.get("executive_summary", "")
    workforce_composition_and_diversity = section_results.get(
        "workforce_composition_and_diversity", ""
    )
    working_conditions_and_equal_opportunity = section_results.get(
        "working_conditions_and_equal_opportunity", ""
    )
    training_and_development = section_results.get("training_and_development", "")
    turnover_and_retention = section_results.get("turnover_and_retention", "")
    health_and_safety = section_results.get("health_and_safety", "")
    outlook_and_next_steps = section_results.get("outlook_and_next_steps", "")
    closing = section_results.get("closing", "")

    return {
        "sections": {
            "executive_summary": executive_summary,
            "workforce_composition_and_diversity": workforce_composition_and_diversity,
            "working_conditions_and_equal_opportunity": working_conditions_and_equal_opportunity,
            "training_and_development": training_and_development,
            "turnover_and_retention": turnover_and_retention,
            "health_and_safety": health_and_safety,
            "outlook_and_next_steps": outlook_and_next_steps,
            "closing": closing,
        },
        "charts": charts,
    }
