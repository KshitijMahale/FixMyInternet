# Internet Problem Analyzer

A web-based network diagnostics tool that analyzes internet connectivity issues and provides actionable recommendations.

Unlike traditional speed testing tools that only display raw speed numbers, **Internet Problem Analyzer identifies potential root causes of slow or unstable internet connections and suggests solutions.**

---

# Overview

Many internet testing tools only provide metrics such as:

* Download speed
* Upload speed
* Latency

However, these numbers do not explain **why** the internet may feel slow or unstable.

Internet Problem Analyzer goes further by performing multiple network diagnostics and generating a **health score and root cause analysis**.

Example output:

```
Internet Health Score: 76 / 100

Detected Issue:
Slow DNS server

Recommended Fix:
Switch DNS to Cloudflare (1.1.1.1)
```

---

# Features

## Speed Test

Measures basic internet performance including:

* Download speed
* Upload speed
* Latency

This establishes a baseline for internet quality.

---

## Multi-Server Latency Test

Measures latency to multiple endpoints such as:

* Google
* Cloudflare
* Amazon

This helps detect:

* routing issues
* ISP congestion
* network instability

---

## DNS Resolution Test

Tests how quickly domain names resolve using different DNS providers.

Providers tested:

* ISP DNS
* Cloudflare DNS (1.1.1.1)
* Google DNS (8.8.8.8)

This helps detect **slow DNS configurations**.

---

## Packet Loss Detection

Detects dropped packets by sending multiple network requests.

High packet loss can indicate:

* unstable WiFi
* network congestion
* hardware problems

---

## Internet Health Score

All diagnostic metrics are combined into a single score.

| Metric      | Weight |
| ----------- | ------ |
| Speed       | 40     |
| Latency     | 20     |
| DNS         | 20     |
| Packet Loss | 20     |

Example:

```
Internet Health Score: 82 / 100
```

---

## Root Cause Detection Engine

The backend analyzes diagnostic results and identifies potential problems.

Example rule:

```
IF DNS latency > 100 ms
AND Cloudflare DNS < 40 ms
```

Diagnosis:

```
Slow ISP DNS
```

Suggested solution:

```
Switch DNS to Cloudflare
```

The system acts as a **network troubleshooting assistant**.

---

# Architecture

The application follows a simple layered architecture.

```
Browser
   ↓
Frontend (HTML + JavaScript)
   ↓
FastAPI Backend
   ↓
Diagnostics Modules
   ↓
Root Cause Analysis Engine
   ↓
PostgreSQL Database
```

---

# Technology Stack

## Backend

* Python
* FastAPI
* ping3
* dnspython
* speedtest-cli
* requests

FastAPI was chosen because it provides:

* high performance
* asynchronous support
* simple API design

---

## Frontend

* HTML
* TailwindCSS
* Vanilla JavaScript

The frontend is intentionally lightweight to ensure fast loading and simplicity.

---

## Database

PostgreSQL

The database stores diagnostic analytics such as:

* speed metrics
* latency
* DNS resolution time
* packet loss
* internet health score
* ISP information
* location data

---

## Deployment

Recommended deployment platforms:

Backend:

* Render
* Railway

Database:

* Supabase (PostgreSQL)

Frontend:

* Render or Vercel

---

# Project Structure

```
internet-problem-analyzer
│
├── backend
│   ├── main.py
│   ├── diagnostics
│   │   ├── speed_test.py
│   │   ├── ping_test.py
│   │   ├── dns_test.py
│   │   └── packet_loss.py
│   │
│   ├── analysis
│   │   └── root_cause_engine.py
│   │
│   └── models
│       └── result_model.py
│
├── frontend
│   ├── index.html
│   ├── css
│   │   └── style.css
│   │
│   └── js
│       └── app.js
│
├── docs
│   ├── architecture.md
│   ├── api.md
│   ├── diagnostics.md
│   ├── scoring-system.md
│   └── roadmap.md
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

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
