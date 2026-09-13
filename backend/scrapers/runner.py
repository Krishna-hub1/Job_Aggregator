from datetime import datetime

from models import db, Job, Company
from scrapers.greenhouse import scrape_greenhouse_company, GREENHOUSE_COMPANIES
from scrapers.lever import scrape_lever_company, LEVER_COMPANIES

COMPANY_WEBSITES = {
    "airbnb": "https://www.airbnb.com",
    "discord": "https://discord.com",
    "figma": "https://www.figma.com",
    "notion": "https://www.notion.com",
    "stripe": "https://stripe.com",
    "cloudflare": "https://www.cloudflare.com",
    "databricks": "https://www.databricks.com",
    "plaid": "https://plaid.com",
    "ramp": "https://ramp.com",
    "netflix": "https://www.netflix.com",
    "spotify": "https://www.spotify.com",
    "twitch": "https://www.twitch.tv",
    "coinbase": "https://www.coinbase.com",
    "robinhood": "https://robinhood.com",
    "google": "https://www.google.com",
    "microsoft": "https://www.microsoft.com",
    "amazon": "https://www.amazon.com",
    "zoho": "https://www.zoho.com",
    "swiggy": "https://www.swiggy.com",
    "tcs": "https://www.tcs.com",
    "accenture": "https://www.accenture.com",
}


def company_website(slug, ats_platform):
    if slug in COMPANY_WEBSITES:
        return COMPANY_WEBSITES[slug]
    return f"https://{slug}.com" if ats_platform == "greenhouse" else f"https://{slug}.com"


def logo_url(website):
    if not website:
        return None
    return f"https://www.google.com/s2/favicons?domain_url={website}&sz=128"


def classify_experience(title):
    title_lower = (title or "").lower()
    if any(kw in title_lower for kw in ["intern", "internship"]): return "intern"
    if any(kw in title_lower for kw in ["junior", "jr.", "entry", "associate", " i ", " i,", " 1 "]): return "entry"
    if any(kw in title_lower for kw in ["senior", "sr.", " iii", " 3 ", "staff", "principal"]): return "senior"
    if any(kw in title_lower for kw in ["lead", "manager", "head of", "director"]): return "lead"
    if any(kw in title_lower for kw in ["vp", "vice president", "chief", "cto", "ceo"]): return "executive"
    return "mid"


def get_or_create_company(name, ats_platform, website=None):
    company = Company.query.filter_by(name=name, ats_platform=ats_platform).first()
    if not company:
        company = Company(name=name, ats_platform=ats_platform, website=website, logo_url=logo_url(website))
        db.session.add(company)
        db.session.flush()
    else:
        if website and company.website != website:
            company.website = website
        if not company.logo_url and website:
            company.logo_url = logo_url(website)
    return company


def run_scrapers():
    started = datetime.utcnow()
    print("\n========== SCRAPE RUN START ==========")
    print(f"Greenhouse boards: {len(GREENHOUSE_COMPANIES)}")
    print(f"Lever sites: {len(LEVER_COMPANIES)}")
    summary = {"sources_attempted": 0, "sources_succeeded": 0, "sources_failed": 0,
               "jobs_fetched": 0, "jobs_inserted": 0, "jobs_updated": 0, "errors": []}

    for slug in GREENHOUSE_COMPANIES:
        summary["sources_attempted"] += 1
        try:
            jobs = scrape_greenhouse_company(slug)
            company_name = slug.replace("-", " ").title()
            if jobs:
                website = company_website(slug, "greenhouse")
                company = get_or_create_company(company_name, "greenhouse", website)
                inserted, updated = save_jobs(company, jobs)
                db.session.commit()
                summary["jobs_fetched"] += len(jobs)
                summary["jobs_inserted"] += inserted
                summary["jobs_updated"] += updated
            summary["sources_succeeded"] += 1
        except Exception as exc:
            db.session.rollback(); summary["sources_failed"] += 1
            summary["errors"].append(f"greenhouse:{slug}: {exc}")
            print(f"[Greenhouse] {slug}: DATABASE/PROCESSING ERROR: {exc}")

    for slug in LEVER_COMPANIES:
        summary["sources_attempted"] += 1
        try:
            jobs = scrape_lever_company(slug)
            company_name = slug.replace("-", " ").title()
            if jobs:
                website = company_website(slug, "lever")
                company = get_or_create_company(company_name, "lever", website)
                inserted, updated = save_jobs(company, jobs)
                db.session.commit()
                summary["jobs_fetched"] += len(jobs)
                summary["jobs_inserted"] += inserted
                summary["jobs_updated"] += updated
            summary["sources_succeeded"] += 1
        except Exception as exc:
            db.session.rollback(); summary["sources_failed"] += 1
            summary["errors"].append(f"lever:{slug}: {exc}")
            print(f"[Lever] {slug}: DATABASE/PROCESSING ERROR: {exc}")

    elapsed = (datetime.utcnow() - started).total_seconds()
    summary["elapsed_seconds"] = round(elapsed, 2)
    summary["database_jobs"] = Job.query.count()
    summary["database_companies"] = Company.query.count()
    print("========== SCRAPE RUN COMPLETE ==========")
    print(summary)
    return summary


def save_jobs(company, jobs):
    inserted = updated = 0
    for job_data in jobs:
        apply_url = job_data.get("apply_url")
        title = (job_data.get("title") or "").strip()
        if not title or not apply_url: continue
        existing = Job.query.filter_by(company_id=company.id, apply_url=apply_url).first()
        values = dict(external_id=job_data.get("external_id"), title=title, location=job_data.get("location"), job_type=job_data.get("job_type"),
                      experience_level=classify_experience(title), salary_min=job_data.get("salary_min"),
                      salary_max=job_data.get("salary_max"), description=job_data.get("description"),
                      remote=bool(job_data.get("remote", False)), posted_at=job_data.get("posted_at"), is_active=True)
        if existing:
            for key, value in values.items(): setattr(existing, key, value)
            updated += 1
        else:
            db.session.add(Job(company_id=company.id, apply_url=apply_url, **values)); inserted += 1
    return inserted, updated
