# FixMyInternet

FixMyInternet is a production-ready web app that runs deep internet diagnostics and explains network issues in human language.

It answers three user questions:
1. How good is my internet connection?
2. What problem is affecting my internet?
3. How can I fix it?

## What It Includes
1. Backend diagnostics engine (FastAPI + Python)
2. Frontend dashboard (HTML + TailwindCSS + Vanilla JS)
3. Root-cause explanation system
4. Health score model and recommendation engine

## Project Structure

```text
FixMyInternet/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── runtime.txt
│   ├── diagnostics/
│   │   ├── ping_test.py
│   │   ├── dns_test.py
│   │   ├── packet_loss.py
│   │   └── speed_test.py
│   └── analysis/
│       └── root_cause_engine.py
├── frontend/
│   ├── index.html
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── app.js
└── README.md
```

## API

### Endpoint

`GET /diagnostics/full-analysis`

### Response Shape

```json
{
   "speed": {
      "download_mbps": 91.23,
      "upload_mbps": 19.85
   },
   "latency": {
      "targets": {},
      "summary": {
         "average_latency_ms": 42.1,
         "minimum_latency_ms": 18.0,
         "maximum_latency_ms": 80.3,
         "variance_ms2": 214.9,
         "jitter_ms": 62.3
      }
   },
   "dns": {
      "servers": {},
      "summary": {
         "average_latency_ms": 35.7,
         "minimum_latency_ms": 15.2,
         "maximum_latency_ms": 90.6,
         "fastest_server": "1.1.1.1"
      }
   },
   "packet_loss": {
      "target": "1.1.1.1",
      "packets_sent": 20,
      "packets_received": 20,
      "packets_lost": 0,
      "packet_loss_percent": 0.0
   },
   "analysis": {
      "health_score": 95,
      "diagnosis": "Connection looks healthy",
      "explanation": "No major internet stability or quality problems were detected during this diagnostic run.",
      "recommendation": "If you still feel slowness, run the test again at a different time and compare trends.",
      "issues_detected": [],
      "jitter_ms": 62.3
   },
   "timestamp": "2026-03-24T10:11:22.000000+00:00"
}
```

## Diagnostics Implemented

1. Latency Test
1. Targets: `8.8.8.8`, `1.1.1.1`, `8.8.4.4`, `9.9.9.9`
1. 5 pings per target using `ping3`
1. Computes average, min, max, variance

1. DNS Test
1. DNS servers: `1.1.1.1`, `8.8.8.8`, `9.9.9.9`
1. 3 queries per server for `google.com` using `dnspython`
1. Computes average latency and fastest server

1. Packet Loss Test
1. 20 pings to `1.1.1.1`
1. Returns packets sent/received/lost and loss percentage

1. Speed Test
1. Uses `speedtest-cli`
1. Returns `download_mbps` and `upload_mbps`

## Root Cause Analysis Rules

1. Slow DNS: `average DNS latency > 120 ms`
1. High Latency: `average latency > 120 ms`
1. Packet Loss: `packet_loss_percent > 5`
1. Low Speed: `download_speed < 5 Mbps`
1. ISP Congestion: `latency > 80 ms AND packet_loss < 1%`
1. WiFi Instability: `jitter > 80 ms`

The engine returns diagnosis + explanation + recommendation in plain language.

## Health Score Algorithm

Score starts at `100` and applies penalties:

Latency:
1. `>150 ms` -> `-30`
1. `80-150 ms` -> `-15`
1. `50-80 ms` -> `-5`

DNS:
1. `>200 ms` -> `-25`
1. `100-200 ms` -> `-15`
1. `60-100 ms` -> `-5`

Packet Loss:
1. `>10%` -> `-40`
1. `5-10%` -> `-25`
1. `2-5%` -> `-10`

Minimum score is `0`.

## Local Setup

### 1) Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 2) Frontend

The frontend is served directly by FastAPI at `/`.

Open:

`http://localhost:8000`

## Deploy Guide

### Render (Recommended)

1. Create a new Web Service from this repository.
2. Set Root Directory to `backend`.
3. Build Command:

```bash
pip install -r requirements.txt
```

4. Start Command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

5. Environment:
1. Python runtime from `runtime.txt`

### Railway

1. Deploy from GitHub.
2. Service root: `backend`.
3. Start command:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Notes for Production

1. ICMP ping may require admin privileges or may be blocked in some cloud networks.
2. If ICMP is blocked, latency and packet-loss measurements may show degraded or missing data.
3. Run diagnostics from user devices for best real-world accuracy.

# Installation

Clone the repository:

```
git clone https://github.com/your-username/internet-problem-analyzer.git
```

Navigate to the project directory:

```
cd internet-problem-analyzer
```

Create a virtual environment:

```
python -m venv venv
```

Activate the virtual environment:

Linux / Mac:

```
source venv/bin/activate
```

Windows:

```
venv\Scripts\activate
```

Install dependencies:

```
pip install -r requirements.txt
```

---

# Running the Backend

Start the FastAPI server:

```
uvicorn backend.main:app --reload
```

Server will run at:

```
http://127.0.0.1:8000
```

API documentation:

```
http://127.0.0.1:8000/docs
```

---

# Documentation

Detailed documentation is available in the `/docs` folder.

| File              | Description                       |
| ----------------- | --------------------------------- |
| architecture.md   | System architecture overview      |
| api.md            | API endpoints and usage           |
| diagnostics.md    | Explanation of diagnostic modules |
| scoring-system.md | Internet health score calculation |
| roadmap.md        | Future development plan           |

---

# Roadmap

## Version 1

Core diagnostics:

* Speed test
* Latency test
* DNS test
* Packet loss detection
* Internet health score

---

## Version 2

Improved analytics:

* interactive charts
* historical results
* ISP performance comparisons

---

## Version 3

Advanced intelligence:

* machine learning for root cause detection
* predictive network diagnostics

---

# Contributing

Contributions are welcome.

Steps:

1. Fork the repository
2. Create a new branch
3. Implement your changes
4. Submit a pull request

Please ensure all contributions include documentation updates when applicable.
