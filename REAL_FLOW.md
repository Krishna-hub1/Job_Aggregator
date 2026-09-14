# Real end-to-end flow

This project is designed to run the real flow, not a fake seed-data test:

`Greenhouse/Lever -> scraper -> MySQL -> Flask GET API -> React/Vite frontend`

## 1. Configure MySQL

Create the database once:

```sql
CREATE DATABASE job_aggregator;
```

Set the credentials in `backend/.env`.

## 2. Start backend

```bash
cd "New folder\backend"
pip install -r requirements.txt
python app.py
```

The server creates the tables and, if the jobs table is empty, starts one real scrape automatically. It then refreshes every 24 hours.

## 3. What to watch in the terminal

A successful run looks like:

```text
Startup database check: 0 jobs currently stored.
Database is empty -> starting initial real scrape.
========== SCRAPE RUN START ==========
[Greenhouse] <company>: fetched <N> jobs
[Lever] <company>: fetched <N> jobs
========== SCRAPE RUN COMPLETE ==========
{'jobs_fetched': ..., 'jobs_inserted': ..., 'database_jobs': ...}
```

A failed source is isolated and printed instead of rolling back jobs from other sources.

## 4. Start frontend

In a second terminal:

```bash
cd "New folder\frontend"
npm install
npm run start
```

Open the Vite URL shown by the terminal, normally `http://localhost:5173`.

The frontend calls `/api/...`; Vite proxies those requests to Flask at `127.0.0.1:5000`.

## 5. Real GET flow

The browser page calls:

`GET /api/stats`

then:

`GET /api/jobs`

The filters call the same GET endpoint with query parameters. The job detail endpoint is also GET.

## Important

The external ATS APIs are live services. If your PC/network/DNS/firewall blocks them, the terminal will explicitly show the failed source. The application itself should remain running and any successful source can still populate MySQL.
