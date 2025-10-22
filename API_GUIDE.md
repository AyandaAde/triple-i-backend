## Overview

This guide contains instructions for how visuals and ESRS S1 references are generated

## Section A: Visual Generation Process

### Matplotlib Chart Templates

The system uses matplotlib to generate charts from KPI data provided to it from the report.py endpoint.

#### 1. Core Chart Functions (`app/report_generator.py`)

**Workforce by Gender Donut Chart** (lines 32-45):
```python
def _plot_workforce_by_gender_pie(workforce_by_gender: List[Dict[str, Any]]) -> str:
    labels = [item.get("gender", "Unknown") for item in workforce_by_gender]
    sizes = [item.get("employee_count", 0) for item in workforce_by_gender]
    
    fig, ax = plt.subplots(figsize=(6, 6))
    wedges, texts = ax.pie(sizes, wedgeprops=dict(width=0.4), startangle=140)
    # Creates donut chart with legend
    centre_circle = plt.Circle((0, 0), 0.70, fc="white")  # Donut hole
    fig.gca().add_artist(centre_circle)
```
+
**Training Hours Bar Chart** (lines 48-60):
```python
def _plot_training_hours_by_gender_bar(training_breakdown: List[Dict[str, Any]]) -> str:
    labels = [item.get("gender", "Unknown") for item in training_breakdown]
    values = [float(item.get("total_training_hours", 0.0)) for item in training_breakdown]
    
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(labels, values, color="#4C78A8")
    ax.set_title("Total Training Hours by Gender")
    ax.grid(axis="y", linestyle=":", alpha=0.5)
```

**Year-over-Year Trend Chart** (lines 63-74):
```python
def _plot_trend_bar(title: str, current_value: float, prior_value: Optional[float]) -> Optional[str]:
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(["Prior"], [prior_value], color="#A0A0A0")
    ax.bar(["Current"], [current_value], color="#59A14F")
    ax.set_title(title)
    ax.grid(axis="y", linestyle=":", alpha=0.5)
```

#### 2. Enhanced Chart Templates (`app/templates/visuals.py`)

The system includes comprehensive chart templates with fallback handling:

**Default Workforce Pie Chart** (lines 15-74):
- Handles empty data scenarios
- Filters out zero values
- Applies consistent styling and colors
- Creates donut chart with percentage labels

**Default Training Hours Chart** (lines 77-132):
- Bar chart with value labels on bars
- Professional styling with grid lines
- Handles missing data gracefully

**Default Trend Chart** (lines 135-189):
- Year-over-year comparison visualization
- Calculates and displays percentage change
- Color-coded for positive/negative trends

**KPI Summary Chart** (lines 192-262):
- Horizontal bar chart for key metrics
- Normalizes values for better visualization
- Includes disability percentage, turnover rate, training hours, injury rate

### Chart Generation Process

1. **Data Extraction**: KPI data is extracted from the database using `kpi_processor.py`
2. **Chart Creation**: Matplotlib functions create figures with specific styling
3. **Base64 Encoding**: Charts are converted to base64 PNG strings using `_fig_to_base64_png()`
4. **Document Embedding**: Base64 images are embedded into DOCX and PDF documents

### Base64 Conversion Process

```python
def _fig_to_base64_png(fig) -> str:
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", bbox_inches="tight", dpi=200)
    plt.close(fig)  # Memory cleanup
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")
```

## Section B: ESRS S1 Reference Generation

### Prompt Template System

#### 1. Section Guidance Mapping (`app/templates/prompts.py`)

Each section is set up to generate prompts to pass into openai with specific ESRS S1 disclosure requirements:

```python
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
```

#### 2. Prompt Building Process

The system creates prompts containing the section-specific guidance, current KPI data in a JSON fromat, optional historical KPI data for trend analysis and the ESRS S1 disclosure requirements.

```python
def _build_section_prompt(
    section_name: str,
    kpi_data: Dict[str, Any],
    historical_kpi_data: Optional[Dict[str, Any]],
) -> str:
    section_guidance = SECTION_GUIDANCE.get(section_name, "Write a professional ESG narrative section.")
    
    return (
        f"You are an ESG reporting analyst. Write the '{section_name}' section for an ESRS S1 Management Report.\n\n"
        f"Requirements: {section_guidance}\n\n"
        f"Current KPI Data:\n{safe(kpi_data)}\n\n"
        f"Historical KPI Data (optional):\n{safe(historical_kpi_data or {})}\n\n"
        "Return only the section text, no JSON wrapper or additional formatting."
    )
```

#### 3. Asynchronous OpenAI Integration

The system uses asynchronous function calls to generate all the narrative sections simultaneously. The system also uses the openai model gpt-4o-mini to optimise for speed with max_completion_tokens set to 2000 and tempereature set to 0.7 to optimise for coherency:

**Async Section Generation** (lines 111-134 in `report_generator.py`):

```python
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
                {"role": "system", "content": "You are an expert ESG (ESRS S1) reporting analyst."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_completion_tokens=2000,
        )
        return completion.choices[0].message.content if completion.choices else ""
    except Exception:
        return ""
```

**Asycnchronous Processing** (lines 187-227):
```python
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
        _generate_section_async(client, section, kpi_data, historical_kpi_data, openai_model)
        for section in sections
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

```

#### 4. ESRS S1 Disclosure Mapping

The system maps the ESRS S1 disclosure requirements generated by report_generator.py into narrative sections:

- **S1-1**: Workforce composition and diversity (workforce_composition_and_diversity)
- **S1-2**: Working conditions (working_conditions_and_equal_opportunity)
- **S1-3**: Equal opportunity (working_conditions_and_equal_opportunity)
- **S1-9**: Diversity and inclusion (workforce_composition_and_diversity)
- **S1-13**: Training and development (training_and_development)
- **S1-14**: Health and safety (health_and_safety)

### Layout Template System

The system then uses a comprehensive layout template system to customize document structure, section titles, and content based on the information passed to it.

#### Layout Configuration (`app/templates/layouts.py`)

```python
DEFAULT_LAYOUT: Dict[str, Any] = {
    "cover_page": {
        "title": "ESRS S1 Management Report",
        "show_date": True,
        "show_confidential": True,
        "show_logo": True,
        "fields": [
            {"label": "Company Name", "key": "company_name"},
            {"label": "Reporting Year", "key": "year"},
        ],
    },
    "kpi_summary": {
        "title": "KPI Summary",
        "description": "Summary of headline KPIs, workforce statistics, and performance metrics.",
        "columns": ["Metric", "Value"],
    },
    "visuals": {
        "title": "KPI Visualizations",
        "chart_order": [
            "workforce_by_gender",
            "training_hours_by_gender",
            "trend_training_hours_per_employee",
            "kpi_summary",
        ],
        "display_mode": "vertical",
    },
    "narrative": {
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
    },
    "closing": {
        "title": "Closing",
        "key": "closing",
        "footer_note": "End of Report — Confidential",
    },
}
```

#### Layout Application in Document Generation

**DOCX Generation** (`app/file_export.py`):
- Cover page configuration: `cover_config.get("title", "ESRS S1 Management Report")`
- KPI summary: `kpi_config.get("title", "KPI Summary")`
- Visualizations: `visuals_config.get("title", "KPI Visualizations")`
- Chart ordering: `visuals_config.get("chart_order", [...])`
- Narrative sections: Dynamic section mapping from `narrative_config.get("sections", [])`
- Closing: `closing_config.get("title", "Closing")`

**PDF Generation** (`app/file_export.py`):
- The same layout structure is applied to ReportLab document generation.
- Cover page elements controlled by `cover_config`
- Chart ordering and titles from `visuals_config`
- Section organization from `narrative_config`

#### Layout Template Function

```python
def get_layout(template_name: str = "default") -> Dict[str, Any]:
    """
    Returns a layout configuration by name.
    Supports multiple templates: default, esrs_s1, etc.
    """
    if template_name.lower() in ("default", "esrs_s1"):
        return DEFAULT_LAYOUT
    raise ValueError(f"Unknown layout template: {template_name}")
```

### Document Embedding Process

#### DOCX Embedding with Layout System

```python
# Narrative sections
narrative_config = layout.get("narrative", {})
sections_config = narrative_config.get("sections", [])

# Create sections mapping
sections_data = {
    "executive_summary": executive_summary,
    "workforce_composition_and_diversity": workforce_composition_and_diversity,
    "working_conditions_and_equal_opportunity": working_conditions_and_equal_opportunity,
    "training_and_development": training_and_development,
    "turnover_and_retention": turnover_and_retention,
    "health_and_safety": health_and_safety,
    "outlook_and_next_steps": outlook_and_next_steps,
}

for section_config in sections_config:
    title = section_config.get("title", "")
    key = section_config.get("key", "")
    content = sections_data.get(key, "")
    
    if title and content:
        if title == "Executive Summary":
            doc.add_heading(title, level=1)
        else:
            doc.add_heading(title, level=3)

        for para in content.split("\n\n"):
            doc.add_paragraph(para)
```

#### PDF Embedding with Layout System

```python
# Narrative sections
narrative_config = layout.get("narrative", {})
sections_config = narrative_config.get("sections", [])

# Create sections mapping
sections_data = {
    "executive_summary": executive_summary,
    "workforce_composition_and_diversity": workforce_composition_and_diversity,
    "working_conditions_and_equal_opportunity": working_conditions_and_equal_opportunity,
    "training_and_development": training_and_development,
    "turnover_and_retention": turnover_and_retention,
    "health_and_safety": health_and_safety,
    "outlook_and_next_steps": outlook_and_next_steps,
}

for section_config in sections_config:
    title = section_config.get("title", "")
    key = section_config.get("key", "")
    content = sections_data.get(key, "")
    
    if title and content:
        if title == "Executive Summary":
            story.append(Paragraph(title, styles["Heading1"]))
        else:
            story.append(Paragraph(title, styles["Heading3"]))

        for para in content.split("\n\n"):
            story.append(Paragraph(para, styles["Normal"]))
            story.append(Spacer(1, 0.1 * inch))
```

## Section C: Data Flow Architecture

### Request Flow Overview

```
POST /report/ → report_generator.py → file_export.py
```

### Detailed Data Flow

#### 1. Request Processing (`app/routers/report.py`)

```python
@router.post("/")
async def create_report(payload: ReportRequest):
    # Extract parameters
    kpi_data = payload.kpi_data
    company_id = payload.company_id
    year = payload.year
    company_name = payload.company_name
    historical_kpi_data = payload.historical_kpi_data
    type = payload.type
    
    # Generate report
    result = await generate_management_report(
        kpi_data=kpi_data,
        historical_kpi_data=historical_kpi_data,
        openai_model="gpt-4o-mini",
        company_id=company_id,
        year=year,
        company_name=company_name,
    )
```

#### 2. Chart Generation Pipeline

```python
# Build visuals from KPI data
charts: Dict[str, Optional[str]] = {
    "workforce_by_gender": None,
    "training_hours_by_gender": None,
    "trend_training_hours_per_employee": None,
}

# Workforce by Gender (pie/donut)
workforce_by_gender = kpi_data.get("Total Workforce by Gender")
if isinstance(workforce_by_gender, list) and workforce_by_gender:
    charts["workforce_by_gender"] = _plot_workforce_by_gender_pie(workforce_by_gender)

# Total Training Hours by Gender (bar)
avg_training = kpi_data.get("Average Training Hours per Employee", {}) or {}
gender_breakdown = avg_training.get("breakdown_by_gender")
if isinstance(gender_breakdown, list) and gender_breakdown:
    charts["training_hours_by_gender"] = _plot_training_hours_by_gender_bar(gender_breakdown)
```

#### 3. Narrative Generation Pipeline

```python
# Build narrative using asynchronous OpenAI API calls
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
        _generate_section_async(client, section, kpi_data, historical_kpi_data, openai_model)
        for section in sections
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)
```

#### 4. Document Assembly Pipeline

```python
# Export files (DOCX and PDF)
docx_filename, docx_b64 = generate_docx_report(
    company_id=company_id,
    year=year,
    company_name=company_name,
    kpi_data=kpi_data,
    charts=charts,
    executive_summary=executive_summary,
    workforce_composition_and_diversity=workforce_composition_and_diversity,
    working_conditions_and_equal_opportunity=working_conditions_and_equal_opportunity,
    training_and_development=training_and_development,
    turnover_and_retention=turnover_and_retention,
    health_and_safety=health_and_safety,
    outlook_and_next_steps=outlook_and_next_steps,
    closing=closing,
    layout_template=layout,
)

pdf_filename, pdf_b64 = generate_pdf_report(
    # Same parameters as DOCX
)
```

### Performance Optimizations

I added in a few things to optimise for performance. 

1. **Asynchronous Processing**: I made the openai API calls asynchronous to have each section generated asynchronously instead of haveing one large API call that generated the entire report using `asyncio.gather()`
2. **OpenAi Model**: I changed the openai gpt model from gpt-5-nano to gpt-4o-mini and reduced the max_completion_tokens to 2000 to optimise for speed and reduced the temperature to 0.7 to optimise for coherency. 
3. **Memory Management**: After creating a matplotlib plot and converting it to a base64 string, I closed out the figures to free up memory.

