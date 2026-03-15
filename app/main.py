from flask import Flask, jsonify
import requests
from datetime import datetime, timezone, timedelta

app = Flask(__name__)

APP_VERSION = "0.0.1"

SENSEBOX_IDS = [
    "5eba5fbad46fb8001b799786",
    "5c21ff8f919bf8001adf2488",
    "5ade1acf223bd80019a1011c",
]

OPENSENSEMAP_URL = "https://api.opensensemap.org/boxes/{box_id}?format=json"

@app.route("/version")
def print_version():
    return jsonify({"version": APP_VERSION})

@app.route("/temperature")
def get_temperature():
    temps = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=1)

    for box_id in SENSEBOX_IDS:
        try:
            response = requests.get(
                OPENSENSEMAP_URL.format(box_id=box_id), timeout=5
            )
            response.raise_for_status()
            sensors = response.json().get("sensors", [])

            for sensor in sensors:
                if "temperatur" in sensor.get("title", "").lower():
                    last = sensor.get("lastMeasurement")
                    if not last:
                        continue
                    measured_at = datetime.fromisoformat(
                        last["createdAt"].replace("Z", "+00:00")
                    )
                    if measured_at < cutoff:
                        continue
                    temps.append(float(last["value"]))
                    break

        except Exception as e:
            print(f"Error fetching box {box_id}: {e}")
            continue

    if not temps:
        return jsonify({"error": "No valid temperature data available"}), 503

    avg = round(sum(temps) / len(temps), 2)
    return jsonify({"temperature": avg, "unit": "celsius", "count": len(temps)})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)