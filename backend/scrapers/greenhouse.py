import os
from datetime import datetime

import requests

TIMEOUT = int(os.getenv("SCRAPER_TIMEOUT", "15"))
HEADERS = {"User-Agent": "JobAggregator/1.0", "Accept": "application/json"}


def scrape_greenhouse_company(company_slug):
    """Fetch published Greenhouse jobs for one board token."""
    url = f"https://boards-api.greenhouse.io/v1/boards/{company_slug}/jobs"
    params = {"content": "true"}

    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"HTTP/network error: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError(f"invalid JSON: {exc}") from exc

    jobs = []
    for raw in data.get("jobs", []):
        title = (raw.get("title") or "").strip()
        apply_url = raw.get("absolute_url")
        if not title or not apply_url:
            continue

        location = (raw.get("location") or {}).get("name") or "Unknown"
        description = raw.get("content") or ""

        jobs.append({
            "external_id": str(raw.get("id")) if raw.get("id") is not None else None,
            "title": title,
            "location": location,
            "remote": "remote" in location.lower(),
            "apply_url": apply_url,
            "description": description,
            "posted_at": parse_date(raw.get("updated_at")),
            "ats_platform": "greenhouse",
        })

    print(f"[Greenhouse] {company_slug}: fetched {len(jobs)} jobs")
    return jobs


def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", "+00:00")).date()
    except (TypeError, ValueError):
        return None


# Board tokens are configurable so stale company slugs can be replaced without code changes.
GREENHOUSE_COMPANIES = [
    item.strip() for item in os.getenv(
        "GREENHOUSE_COMPANIES",
        "airbnb,discord,figma,notion,stripe,cloudflare,databricks,plaid,ramp",
    ).split(",") if item.strip()
]
