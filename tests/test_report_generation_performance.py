"""
Tests the performance of the generate_management_report function and ensures
it completes within 10 seconds.

"""

import time
import pytest
from app.report_generator import generate_management_report
from tests.conftest import SAMPLE_HISTORICAL_KPI_DATA, SAMPLE_KPI_DATA


class TestReportGenerationPerformance:

    @pytest.mark.asyncio
    async def test_generate_management_report(
        self
    ):
        import time

        start_time = time.time()

        result = await generate_management_report(
            kpi_data=SAMPLE_KPI_DATA,
            historical_kpi_data=SAMPLE_HISTORICAL_KPI_DATA
        )

        end_time = time.time()
        generation_time = end_time - start_time

        assert (
            generation_time < 10.0
        ), f"Report generation took {generation_time:.2f} seconds, expected < 10 seconds"

        assert isinstance(result, dict), "Function did not return a dictionary"
