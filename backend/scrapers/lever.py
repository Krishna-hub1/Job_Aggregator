import os
from datetime import datetime, timezone

import requests

TIMEOUT = int(os.getenv("SCRAPER_TIMEOUT", "15"))
HEADERS = {"User-Agent": "JobAggregator/1.0", "Accept": "application/json"}


def scrape_lever_company(company_slug):
    """Fetch published Lever jobs for one site."""
    url = f"https://api.lever.co/v0/postings/{company_slug}"
    params = {"mode": "json"}

    try:
        response = requests.get(url, params=params, headers=HEADERS, timeout=TIMEOUT)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        raise RuntimeError(f"HTTP/network error: {exc}") from exc
    except ValueError as exc:
        raise RuntimeError(f"invalid JSON: {exc}") from exc

    jobs = []
    for raw in data if isinstance(data, list) else []:
        title = (raw.get("text") or "").strip()
        apply_url = raw.get("applyUrl") or raw.get("hostedUrl")
        if not title or not apply_url:
            continue

        categories = raw.get("categories") or {}
        location = categories.get("location") or "Unknown"
        workplace = (raw.get("workplaceType") or "").lower()
        description = raw.get("description") or raw.get("descriptionPlain") or ""
        salary = raw.get("salaryRange") or {}

        jobs.append({
            "external_id": raw.get("id"),
            "title": title,
            "location": location,
            "remote": workplace == "remote" or "remote" in location.lower(),
            "apply_url": apply_url,
            "description": description,
            "job_type": map_commitment(categories.get("commitment", "")),
            "salary_min": to_int(salary.get("min")),
            "salary_max": to_int(salary.get("max")),
            "posted_at": parse_timestamp(raw.get("createdAt")),
            "ats_platform": "lever",
        })

    print(f"[Lever] {company_slug}: fetched {len(jobs)} jobs")
    return jobs


def to_int(value):
    try:
        return int(value) if value is not None else None
    except (TypeError, ValueError):
        return None


def parse_timestamp(value):
    if value is None:
        return None
    try:
        return datetime.fromtimestamp(int(value) / 1000, tz=timezone.utc).date()
    except (TypeError, ValueError, OverflowError):
        return None


def map_commitment(commitment):
    value = (commitment or "").lower()
    if "full" in value:
        return "full-time"
    if "part" in value:
        return "part-time"
    if "contract" in value:
        return "contract"
    if "intern" in value:
        return "internship"
    return None


LEVER_COMPANIES = [
    item.strip() for item in os.getenv(
        "LEVER_COMPANIES",
        "netflix,spotify,twitch,coinbase,robinhood",
    ).split(",") if item.strip()
]
