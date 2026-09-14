# JobHub

JobHub is a job aggregation platform using Python scrapers, MySQL, Flask REST APIs, and React/Vite.

## Architecture

Greenhouse / Lever
→ Python Scrapers
→ MySQL
→ Flask REST API
→ React / Vite

## Run locally

### 1. MySQL
Create the database:

```sql
CREATE DATABASE job_aggregator;
```

Configure `backend/.env` using `backend/.env.example`.

### 2. Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

API: http://127.0.0.1:5000

### 3. Frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run start
```

Frontend: http://localhost:5173

## Scraper

The scraper code is under `backend/scrapers/`. The application can perform the configured scheduled refresh, and `backend/run_scraper.py` can be used for a separate scheduled job.

## No Docker

This version intentionally removes Docker Compose, Dockerfiles, and the Nginx container configuration. All components run directly on the host machine.
