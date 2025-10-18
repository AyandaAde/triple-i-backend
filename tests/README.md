# Test Suite for Triple-I Backend

This directory contains comprehensive automated tests for the report generation and file export functionality of the triple-i-backend application.

## Test Structure

### Test Files

- **`conftest.py`** - Pytest configuration and shared fixtures
- **`test_file_export.py`** - Tests for PDF and DOCX file generation
- **`test_report_generation.py`** - Tests for report generation logic
- **`test_integration.py`** - End-to-end integration tests
- **`test_performance_benchmarks.py`** - Performance benchmark tests
- **`test_utils.py`** - Utility functions and helpers for testing

### Test Categories

#### 1. Performance Tests
- **Generation Speed**: Verify report generation completes within 10 seconds
- **File Export Speed**: Verify PDF/DOCX generation completes within 10 seconds
- **Concurrent Processing**: Test multiple reports generated simultaneously
- **Large Dataset Handling**: Test performance with extensive KPI data

#### 2. Validation Tests
- **File Validity**: Ensure generated files are valid and non-empty
- **Content Verification**: Check that files contain expected content
- **Format Compliance**: Validate PDF and DOCX file formats
- **Error Handling**: Test graceful handling of edge cases and errors

#### 3. ESRS S1 Compliance Tests
- **Required Sections**: Verify all ESRS S1 sections are present
- **KPI Integration**: Check that KPI data is properly integrated
- **Visual Elements**: Validate presence of charts and visualizations
- **Tag Validation**: Ensure ESRS S1 tags and references are included

#### 4. Integration Tests
- **End-to-End Workflow**: Test complete report generation process
- **API Integration**: Test report generation through API endpoints
- **Data Flow**: Verify data flows correctly through all components
- **Error Recovery**: Test system recovery from various error conditions

## Running Tests

### Prerequisites

Install test dependencies:
```bash
pip install pytest pytest-asyncio pytest-cov PyPDF2
```

### Basic Test Execution

Run all tests:
```bash
python run_tests.py
```

Run specific test types:
```bash
# Unit tests only
python run_tests.py --type unit

# Integration tests only
python run_tests.py --type integration

# Performance tests only
python run_tests.py --type performance
```

### Advanced Options

Run with coverage report:
```bash
python run_tests.py --coverage
```

Run in non-verbose mode:
```bash
python run_tests.py --no-verbose
```

### Direct Pytest Usage

Run specific test files:
```bash
pytest tests/test_file_export.py -v
pytest tests/test_report_generation.py -v
pytest tests/test_integration.py -v
```

Run tests with specific markers:
```bash
pytest -m performance -v
pytest -m integration -v
```

## Test Requirements

### Performance Requirements
- Report generation must complete within 10 seconds
- File export (PDF/DOCX) must complete within 10 seconds
- Concurrent report generation should scale reasonably
- Large datasets should not significantly impact performance

### Validation Requirements
- Generated files must be valid and non-empty
- PDF files must be readable and contain expected content
- DOCX files must be readable and contain expected content
- All required ESRS S1 sections must be present

### ESRS S1 Compliance Requirements
- All required sections must be present:
  - Executive Summary
  - Workforce Composition and Diversity
  - Working Conditions and Equal Opportunity
  - Training and Development
  - Turnover and Retention
  - Health and Safety
  - Outlook and Next Steps
  - Closing
- KPI data must be properly integrated
- Visual elements (charts) must be present when data is available
- ESRS S1 tags and references must be included

## Test Data

### Sample KPI Data
The tests use comprehensive sample KPI data including:
- Employee disability percentages
- Turnover rates by gender
- Training hours breakdown
- Workplace injury rates
- Workforce composition by gender and age
- Historical data for trend analysis

### Mock Services
- OpenAI API calls are mocked to avoid external dependencies
- Chart generation is tested with sample base64 image data
- Database operations are mocked where necessary

## Continuous Integration

The test suite is designed to run in CI/CD pipelines:
- All tests must pass before deployment
- Performance benchmarks ensure system meets requirements
- Coverage reports track test completeness
- Integration tests verify end-to-end functionality

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all dependencies are installed
2. **Async Test Failures**: Check that pytest-asyncio is installed
3. **Performance Test Failures**: Verify system resources are adequate
4. **File Validation Errors**: Check that generated files are not corrupted

### Debug Mode

Run tests with maximum verbosity:
```bash
pytest -vvv --tb=long
```

Run specific test with debugging:
```bash
pytest tests/test_file_export.py::TestFileExportPerformance::test_docx_generation_under_10_seconds -vvv -s
```

## Contributing

When adding new tests:
1. Follow the existing naming conventions
2. Add appropriate test markers
3. Include performance assertions where relevant
4. Update this README if adding new test categories
5. Ensure tests are deterministic and don't depend on external services
