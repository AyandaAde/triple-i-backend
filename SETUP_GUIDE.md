# Triple-I Backend - Setup and Usage Guide

## Overview

This FastAPI backend service generates ESRS S1 Management Reports from workforce data. It processes Excel files containing ESRS S1 data, generates KPI visualizations, creates AI-powered narrative sections, and exports professional reports in DOCX and PDF formats.

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- OpenAI API key

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd triple-i-backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

Create a `.env` file in the root directory:

```env
OPENAI_API_KEY=your_openai_api_key_here
```

**Important**: Replace `your_openai_api_key_here` with your actual OpenAI API key.

### 5. Database Setup

The application uses SQLite database which is automatically created on first run. No additional setup required.

## Running the Application

### Start the FastAPI Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## API Endpoints

### 1. Upload Endpoint

**POST** `/upload/`

Uploads an Excel file containing ESRS S1 workforce data and processes it into the database.

#### Request
- **Content-Type**: `multipart/form-data`
- **Body**: Excel file (.xlsx) with ESRS S1 data sheets

#### Expected Excel Structure
The Excel file should contain sheets with the following data structures:

**Workforce Composition Sheet:**
- `workforceid`, `datekey`, `workforcecount`, `companyid`, `countryid`, `organizationalunitid`, `createdat`, `updatedat`

**Diversity Sheet:**
- `DiversityID`, `DateKey`, `CountryID`, `CompanyID`, `DisabilityCount`, `OrganizationalUnitID`, `created_at`, `updated_at`

**Employee Training Sheet:**
- `trainingid`, `datekey`, `totaltraininghours`, `companyid`, `countryid`, `organizationalunitid`, `createdat`, `updatedat`

**Employee Turnover Sheet:**
- `turnoverid`, `datekey`, `genderid`, `agegroupid`, `employeesdeparted`, `companyid`, `contracttypeid`, `countryid`, `organizationalunitid`, `createdat`, `updatedat`

**Workplace Injuries Sheet:**
- `injuryid`, `datekey`, `injurycount`, `companyid`, `countryid`, `organizationalunitid`, `createdat`, `updatedat`

#### Response
```json
{
  "message": "Excel processed successfully",
  "processed_sheets": ["workforce", "diversity", "training"],
  "skipped_sheets": [],
  "kpi_result": {
    "Total Workforce by Gender": [...],
    "Percentage of Employees with Disabilities": {...},
    "Employee Turnover Rate": {...},
    "Average Training Hours per Employee": {...},
    "Workplace Injury Rate": {...}
  }
}
```

### 2. Report Generation Endpoint

**POST** `/report/`

Generates a comprehensive ESRS S1 Management Report with visualizations and AI-generated narrative sections.

#### Request Body
```json
{
  "company_id": 1,
  "year": 2024,
  "company_name": "Example Company Ltd",
  "kpi_data": {
    "Total Workforce by Gender": [
      {"gender": "Male", "employee_count": 150},
      {"gender": "Female", "employee_count": 120}
    ],
    "Percentage of Employees with Disabilities": {
      "overall_percentage": 5.2,
      "total_employees": 270,
      "total_employees_with_disabilities": 14
    },
    "Employee Turnover Rate": {
      "overall_turnover_rate": 8.5,
      "total_employees": 270,
      "total_employees_departed": 23
    },
    "Average Training Hours per Employee": {
      "overall_average_hours": 24.5,
      "total_employees": 270,
      "total_training_hours": 6615
    },
    "Workplace Injury Rate": {
      "overall_injury_rate": 0.02,
      "total_employees": 270,
      "total_injuries": 5
    }
  },
  "historical_kpi_data": {
    "Average Training Hours per Employee": {
      "overall_average_hours": 22.1
    }
  }
}
```

#### Response
```json
{
  "sections": {
    "executive_summary": "AI-generated executive summary...",
    "workforce_composition_and_diversity": "AI-generated analysis...",
    "working_conditions_and_equal_opportunity": "AI-generated analysis...",
    "training_and_development": "AI-generated analysis...",
    "turnover_and_retention": "AI-generated analysis...",
    "health_and_safety": "AI-generated analysis...",
    "outlook_and_next_steps": "AI-generated recommendations...",
    "closing": "AI-generated closing statement..."
  },
  "charts": {
    "workforce_by_gender": "base64_encoded_png_chart",
    "training_hours_by_gender": "base64_encoded_png_chart",
    "trend_training_hours_per_employee": "base64_encoded_png_chart"
  },
  "files": {
    "docx": {
      "filename": "S1_Report_1_2024.docx",
      "base64": "base64_encoded_docx_content"
    },
    "pdf": {
      "filename": "S1_Report_1_2024.pdf",
      "base64": "base64_encoded_pdf_content"
    }
  }
}
```

## Usage Examples

### 1. Upload Data and Generate Report

```python
import requests
import json

# Step 1: Upload Excel file
with open('workforce_data.xlsx', 'rb') as f:
    files = {'file': f}
    upload_response = requests.post('http://localhost:8000/upload/', files=files)
    upload_data = upload_response.json()

# Step 2: Generate report using KPI data from upload
report_payload = {
    "company_id": 1,
    "year": 2024,
    "company_name": "Your Company Name",
    "kpi_data": upload_data["kpi_result"]
}

report_response = requests.post(
    'http://localhost:8000/report/',
    json=report_payload
)
report_data = report_response.json()

# Step 3: Save generated files
import base64

# Save DOCX file
docx_content = base64.b64decode(report_data["files"]["docx"]["base64"])
with open("report.docx", "wb") as f:
    f.write(docx_content)

# Save PDF file
pdf_content = base64.b64decode(report_data["files"]["pdf"]["base64"])
with open("report.pdf", "wb") as f:
    f.write(pdf_content)
```

### 2. Using cURL

```bash
# Upload file
curl -X POST "http://localhost:8000/upload/" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@workforce_data.xlsx"

# Generate report
curl -X POST "http://localhost:8000/report/" \
  -H "Content-Type: application/json" \
  -d '{
    "company_id": 1,
    "year": 2024,
    "company_name": "Example Company",
    "kpi_data": {
      "Total Workforce by Gender": [
        {"gender": "Male", "employee_count": 150},
        {"gender": "Female", "employee_count": 120}
      ]
    }
  }'
```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Ensure your `.env` file contains a valid `OPENAI_API_KEY`
   - Verify the API key has sufficient credits

2. **Excel File Format Error**
   - Ensure the Excel file has the correct column names
   - Check that all required sheets are present
   - Verify the file is saved as `.xlsx` format

3. **Database Connection Issues**
   - Ensure the application has write permissions in the directory
   - Check that SQLite is properly installed

4. **Memory Issues with Large Files**
   - For large Excel files, consider processing in smaller batches
   - Monitor system memory usage during processing

### Logs and Debugging

The application logs processing information to the console. Key log messages include:
- "Connected to the API." - Upload endpoint accessed
- "Processing sheet: [sheet_name]" - Excel sheet being processed
- "Matched '[sheet_name]' → [ModelClass]" - Data model matching

## Support

For technical support or questions about the API, please refer to the API documentation at http://localhost:8000/docs when the server is running.
