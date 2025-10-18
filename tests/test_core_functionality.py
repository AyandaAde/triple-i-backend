"""
Test core functionality of the report generation system.

This file contains shared fixtures and utilities for the test suite.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)