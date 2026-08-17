"""Flask API for Smart House Water Consumption dashboard."""

import os
import threading
import time

import config  # noqa: F401 — loads .env from project root
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from analytics import consumption_summary, hourly_peak_usage, quality_status, roi_estimate
from database import get_recent_alerts, get_recent_readings, init_db
from fetch_thingspeak import sync_from_thingspeak

app = Flask(__name__, static_folder="../frontend")
CORS(app)

FETCH_INTERVAL = int(os.getenv("FETCH_INTERVAL", "60"))


def background_sync():
    while True:
        try:
            sync_from_thingspeak()
        except Exception as exc:
            print(f"Sync error: {exc}")
        time.sleep(FETCH_INTERVAL)


@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)


@app.route("/api/readings")
def api_readings():
    limit = int(os.getenv("API_READINGS_LIMIT", "100"))
    return jsonify(get_recent_readings(limit))


@app.route("/api/summary")
def api_summary():
    return jsonify(consumption_summary())


@app.route("/api/peaks")
def api_peaks():
    return jsonify(hourly_peak_usage())


@app.route("/api/quality")
def api_quality():
    return jsonify(quality_status())


@app.route("/api/alerts")
def api_alerts():
    return jsonify(get_recent_alerts())


@app.route("/api/roi")
def api_roi():
    return jsonify(roi_estimate())


@app.route("/api/sync", methods=["POST"])
def api_sync():
    try:
        count = sync_from_thingspeak()
        return jsonify({"status": "ok", "synced": count})
    except Exception as exc:
        return jsonify({"status": "error", "message": str(exc)}), 500


if __name__ == "__main__":
    init_db()
    threading.Thread(target=background_sync, daemon=True).start()
    print("Dashboard: http://127.0.0.1:5000")
    app.run(debug=True, port=5000, use_reloader=False)
