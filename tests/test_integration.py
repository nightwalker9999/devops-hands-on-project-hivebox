import pytest
from unittest.mock import patch
from app.main import app

@pytest.fixture
def client():
    app.testing = True
    return app.test_client()

MOCK_BOX_DATA = {
    "sensors": [
        {
            "title": "Temperatur",
            "lastMeasurement": {
                "createdAt": "2099-01-01T00:00:00.000Z",
                "value": "25.0"
            }
        }
    ]
}


def test_version_endpoint_shape(client):
    response = client.get("/version")
    assert response.status_code == 200
    data = response.get_json()
    assert "version" in data

def test_temperature_endpoint_returns_valid_structure(client):
    with patch("app.main.fetch_box_data", return_value=MOCK_BOX_DATA):
        response = client.get("/temperature")
        assert response.status_code == 200
        data = response.get_json()
        assert "temperature" in data
        assert "unit" in data
        assert "count" in data
        assert data["unit"] == "celsius"
        assert isinstance(data["temperature"], float)


def test_temperature_endpoint_503_when_all_boxes_fail(client):
    with patch("app.main.fetch_box_data", side_effect=Exception("API down")):
        response = client.get("/temperature")
        assert response.status_code == 503


def test_metrics_endpoint_returns_200(client):
    response = client.get("/metrics")
    assert response.status_code == 200
    