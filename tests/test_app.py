import pytest
from unittest.mock import patch
from datetime import datetime, timezone, timedelta
from app.main import app, extract_recent_temperature

@pytest.fixture 
def client():
    app.testing = True
    return app.test_client()

# --- /version ---

def test_version_returns_200(client):
    response = client.get("/version")
    assert response.status_code == 200

def test_version_returns_correct_version(client):
    response = client.get("/version")
    data = response.get_json()
    assert data["version"] == "0.0.1"

# --- /temperature ---

MOCK_SENSORS = [
    {
        "title": "Temperatur",
        "lastMeasurement": {
            "createdAt": (datetime.now(timezone.utc) - timedelta(minutes=10)).strftime("%Y-%m-%dT%H:%M:%S.000Z"),    
            "value": "22.5"
        }
    }
]

def test_temperature_returns_200(client):
    with patch("app.main.get_sensors", return_value=MOCK_SENSORS):
        response = client.get("/temperature")
        assert response.status_code == 200

def test_temperature_returns_avg(client):
    with patch("app.main.get_sensors", return_value=MOCK_SENSORS):
        response = client.get("/temperature")
        data = response.get_json()
        assert data["temperature"] == 22.5
        assert data["unit"] == "celsius"
        assert data["count"] == 3

def test_temperature_503_when_no_data(client):
    with patch("app.main.get_sensors", return_value=[]):
        response = client.get("/temperature")
        assert response.status_code == 503

# --- extract_recent_temperature (unit tests) ---


def test_extract_returns_none_for_old_data():
    cutoff = datetime.now(timezone.utc)
    sensors = [
        {
            "title": "Temperatur",
            "lastMeasurement": {
                "createdAt": (cutoff - timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "value": "20.0"
            }
        }
    ]

    result = extract_recent_temperature(sensors, cutoff)
    assert result is None

def test_extract_return_for_wrong_sensor_title():
    cutoff = datetime.now(timezone.utc) - timedelta(hours=1)
    sensors = [
        {
            "title": "Humidity",
            "lastMeasurement": {
                "createdAt": (cutoff - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S.000Z"),
                "value": "20.0" 
            }
        }
    ]

    result = extract_recent_temperature(sensors, cutoff)
    assert result is None

