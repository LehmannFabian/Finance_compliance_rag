from fastapi.testclient import TestClient
import pytest

from src.main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)
