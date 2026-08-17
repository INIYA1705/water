"""
Simulate IoT sensor data and post to ThingSpeak.

Field mapping (Smart House water consumption channel):
  Field 1 - Water Consumption (liters, cumulative)
  Field 2 - Flow Rate (L/min)
  Field 3 - Water Pressure (bar)
  Field 4 - Leak Status (0 = no leak, 1 = leak detected)
  Field 5 - pH
  Field 6 - Turbidity (NTU)

Run until hardware arrives:
  python simulation/thingspeak_sim.py
"""

import os
import random
import time
from datetime import datetime

import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

WRITE_API_KEY = os.getenv("THINGSPEAK_WRITE_API_KEY")
CHANNEL_ID = os.getenv("THINGSPEAK_CHANNEL_ID")
POST_INTERVAL = int(os.getenv("SIM_INTERVAL_SECONDS", "60"))

# Simulated household state
total_consumption = 1250.0
leak_active = False


def simulate_usage_pattern(hour: int) -> float:
    """Return flow rate (L/min) based on time of day."""
    if 6 <= hour <= 8:
        return random.uniform(8, 15)   # morning peak
    if 18 <= hour <= 21:
        return random.uniform(10, 18)  # evening peak
    if 0 <= hour <= 5:
        return random.uniform(0, 0.3)  # night — low usage
    return random.uniform(0, 4)


def detect_leak(flow_rate: float, hour: int) -> int:
    """Leak if abnormal flow at night or very high continuous flow."""
    global leak_active
    if hour <= 5 and flow_rate > 0.5:
        leak_active = True
    elif flow_rate > 20:
        leak_active = True
    elif flow_rate < 0.2 and random.random() > 0.95:
        leak_active = False
    return 1 if leak_active else 0


def generate_reading():
    global total_consumption

    now = datetime.now()
    hour = now.hour

    flow_rate = round(simulate_usage_pattern(hour), 2)
    total_consumption += flow_rate * (POST_INTERVAL / 60)
    pressure = round(random.uniform(2.5, 4.0) - (0.3 if leak_active else 0), 2)
    leak_status = detect_leak(flow_rate, hour)
    ph = round(random.uniform(6.8, 7.8), 2)
    turbidity = round(random.uniform(0.5, 2.5), 2)

    return {
        "field1": round(total_consumption, 1),
        "field2": flow_rate,
        "field3": pressure,
        "field4": leak_status,
        "field5": ph,
        "field6": turbidity,
    }


def post_to_thingspeak(data: dict) -> bool:
    if not WRITE_API_KEY:
        print("ERROR: Set THINGSPEAK_WRITE_API_KEY in .env")
        return False

    url = "https://api.thingspeak.com/update"
    params = {"api_key": WRITE_API_KEY, **data}

    try:
        response = requests.get(url, params=params, timeout=15)
        if response.status_code == 200 and response.text != "0":
            print(
                f"[{datetime.now():%H:%M:%S}] Posted entry #{response.text} | "
                f"Consumption={data['field1']}L Flow={data['field2']}L/min "
                f"Pressure={data['field3']}bar Leak={data['field4']}"
            )
            return True
        print(f"ThingSpeak rejected update: {response.text}")
        return False
    except requests.RequestException as exc:
        print(f"Network error: {exc}")
        return False


def main():
    print("=" * 55)
    print("  Smart House Water Consumption — Sensor Simulator")
    print("=" * 55)
    print(f"Channel ID : {CHANNEL_ID or '(set in .env)'}")
    print(f"Interval   : every {POST_INTERVAL} seconds")
    print("Press Ctrl+C to stop\n")

    if not WRITE_API_KEY:
        print("Create .env from .env.example and add your Write API Key.")
        return

    while True:
        post_to_thingspeak(generate_reading())
        time.sleep(POST_INTERVAL)


if __name__ == "__main__":
    main()
