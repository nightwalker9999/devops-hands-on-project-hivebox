import pytest
from unittest.mock import patch
from app.main import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

MOCK_SENSORS = [
    {
        "title": "Temperatur",
        "lastMeasurement": {
            "createdAt": "2099-01-01T00:00:00.000Z",
            "value": "22.5"
        }
    }
]

def test_version_returns_200(client):
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.get_json()

def test_metrics_returns_200(client):
    response = client.get("/metrics")
    assert response.status_code == 200

def test_temperature_returns_200(client):
    with patch("app.main.get_sensors", return_value=MOCK_SENSORS):
        response = client.get("/temperature")
        assert response.status_code == 200
        data = response.get_json()
        assert "temperature" in data
        assert data["unit"] == "celsius"

def test_temperature_503_when_api_fails(client):
    with patch("app.main.fetch_box_data", side_effect=Exception("API down")):
        response = client.get("/temperature")
        assert response.status_code == 503