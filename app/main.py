import requests
from datetime import datetime, timezone, timedelta
from prometheus_flask_exporter import PrometheusMetrics
from flask import Flask, jsonify, current_app
import os

app = Flask(__name__)
metrics = PrometheusMetrics(app)

APP_VERSION = "0.0.1"

SENSEBOX_IDS = os.getenv(
    "SENSEBOX_IDS",
    "5eba5fbad46fb8001b799786,5c21ff8f919bf8001adf2488,5ade1acf223bd80019a1011c"
).split(",")

OPENSENSEMAP_URL = "https://api.opensensemap.org/boxes/{box_id}?format=json"

def get_temperature_avg(avg):
    if avg < 10:
        return "Too Cold"
    elif avg <=36:
        return "Good"
    else:
        print("Too Hot")

@app.route("/version")
def print_version():
    return jsonify({"version": APP_VERSION})

@app.route("/temperature")
def get_temperature():
    temps = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=1)

    try:
        for box_id in SENSEBOX_IDS:
            sensors = get_sensors(box_id=box_id)
            temperature = extract_recent_temperature(sensors, cutoff)

            if temperature is not None:
                temps.append(temperature)
                
    except Exception:
        current_app.logger.exception("External API error while fetching temperature data")
        return jsonify({"error": "External API unavailable"}), 503  
          
    if not temps:
        return jsonify({"error": "No temperature found"}), 503
            
    avg = round(sum(temps) / len(temps), 2)
    return jsonify({
        "temperature": avg,
        "unit": "celsius",
        "count": len(temps),
        "status": get_temperature_avg(avg)
        })


def fetch_box_data(box_id):
    response = requests.get(OPENSENSEMAP_URL.format(box_id=box_id), timeout=5)
    response.raise_for_status()
    return response.json()


def get_sensors(box_id):
        box_data = fetch_box_data(box_id)
        return box_data.get("sensors", [])

def extract_recent_temperature(sensors, cutoff):
    for sensor in sensors:

        title = sensor.get("title")

        if "Temperatur" not in title:
            continue

        last_measurement = sensor.get("lastMeasurement")
        if not last_measurement:
            continue

        measured_at = datetime.fromisoformat(
            last_measurement.get("createdAt").replace("Z", "+00:00")
            )
        if measured_at < cutoff:
            continue

        return float(last_measurement.get("value"))
    
    return None


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)