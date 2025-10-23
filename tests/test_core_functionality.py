"""
Tests core functionality of the report generation system.

"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)