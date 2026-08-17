# Smart House Water Consumption

**Final Year Project:** Water Consumption Analysis in Smart Cities Using Data Analysis in IoT Sensor  
**Scope:** 1 household  
**Cloud:** ThingSpeak

## ThingSpeak Field Mapping

| Field | Name | Unit | Description |
|-------|------|------|-------------|
| Field 1 | Water Consumption | Liters | Cumulative total usage |
| Field 2 | Flow Rate | L/min | Current flow |
| Field 3 | Water Pressure | bar | Pipe pressure |
| Field 4 | Leak Status | 0 or 1 | 0 = normal, 1 = leak |
| Field 5 | pH | pH | Water quality |
| Field 6 | Turbidity | NTU | Water clarity |

## Setup (do this once)

### 1. Install Python dependencies

```bash
cd d:\Finalyearproject\waterconsumption
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure ThingSpeak keys

Copy `.env.example` to `.env` and fill in your keys from [ThingSpeak Channel Settings](https://thingspeak.com):

```
THINGSPEAK_CHANNEL_ID=1234567
THINGSPEAK_READ_API_KEY=your_read_key
THINGSPEAK_WRITE_API_KEY=your_write_key
```

## What to run while waiting for hardware

Open **3 terminals**:

### Terminal 1 — Simulate sensor data (posts to ThingSpeak)

```bash
python simulation/thingspeak_sim.py
```

This sends realistic household water data every 60 seconds.

### Terminal 2 — Backend API + auto-sync from ThingSpeak

```bash
python backend/api.py
```

### Terminal 3 — Browser

Open: **http://127.0.0.1:5000**

You will see live charts, alerts, quality status, and ROI estimate.

## Project Structure

```
waterconsumption/
├── simulation/thingspeak_sim.py   # Fake sensor (until ESP32 arrives)
├── backend/
│   ├── api.py                     # Flask REST API + dashboard server
│   ├── fetch_thingspeak.py        # Pull data from ThingSpeak → SQLite
│   ├── analytics.py               # Consumption analysis, peaks, ROI
│   └── database.py                # Local database
├── frontend/                      # Web dashboard (Chart.js)
├── hardware/                      # ESP32 code (add when hardware arrives)
├── data/                          # SQLite database (auto-created)
└── docs/                          # Put report chapters here
```

## When hardware arrives

1. Wire ESP32 to flow sensor, pressure sensor, pH, turbidity, leak detector
2. Flash code from `hardware/esp32_thingspeak.ino` (to be added)
3. **Stop** the simulation script
4. Hardware posts to the **same ThingSpeak channel** — dashboard works unchanged

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/readings` | Recent sensor readings |
| `GET /api/summary` | Consumption totals, averages, cost |
| `GET /api/peaks` | Hourly peak usage |
| `GET /api/quality` | pH, turbidity, leak status |
| `GET /api/alerts` | Leak and quality alerts |
| `GET /api/roi` | ROI estimate for 1 house |
| `POST /api/sync` | Manual sync from ThingSpeak |

## Report screenshots to capture

1. ThingSpeak channel graph (all 6 fields)
2. Dashboard — consumption chart
3. Dashboard — peak usage by hour
4. Dashboard — leak alert
5. System architecture diagram (ThingSpeak → Backend → Dashboard)

## Data flow

```
ESP32 / Simulator → ThingSpeak Cloud → Backend (fetch) → SQLite → Analytics → Dashboard
```
