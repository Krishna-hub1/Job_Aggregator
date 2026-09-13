from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import or_, func
from models import Company, Job, SavedJob, User, JobAlert, db

jobs_bp = Blueprint("jobs", __name__)
ALLOWED_STATUS = {"saved", "applied", "interviewing", "rejected", "offer"}

# Common country names/aliases used by ATS location strings. The scraper keeps the
# original location text, so this helper is intentionally tolerant of formats such
# as "Berlin, Germany; Munich, Germany" and "New York, United States".
COUNTRY_ALIASES = {
    "usa": "United States", "us": "United States", "u.s.": "United States",
    "united states": "United States", "united states of america": "United States",
    "uk": "United Kingdom", "u.k.": "United Kingdom", "united kingdom": "United Kingdom",
    "india": "India", "canada": "Canada", "germany": "Germany",
    "netherlands": "Netherlands", "australia": "Australia", "singapore": "Singapore",
    "ireland": "Ireland", "france": "France", "spain": "Spain", "italy": "Italy",
    "switzerland": "Switzerland", "sweden": "Sweden", "denmark": "Denmark",
    "norway": "Norway", "finland": "Finland", "poland": "Poland",
    "belgium": "Belgium", "austria": "Austria", "portugal": "Portugal",
    "israel": "Israel", "japan": "Japan", "china": "China",
    "south korea": "South Korea", "new zealand": "New Zealand",
    "united arab emirates": "United Arab Emirates", "uae": "United Arab Emirates",
}


def normalize_country(value):
    key = " ".join((value or "").strip().lower().split())
    return COUNTRY_ALIASES.get(key)


def extract_country(location):
    text = (location or "").strip()
    if not text:
        return None
    # Most ATS feeds put country after the final comma.
    parts = [part.strip() for part in text.split(",") if part.strip()]
    for part in reversed(parts):
        country = normalize_country(part)
        if country:
            return country
    lower = text.lower()
    for alias, country in sorted(COUNTRY_ALIASES.items(), key=lambda x: len(x[0]), reverse=True):
        if alias in lower:
            return country
    return None


def split_locations(location):
    text = (location or "").strip()
    if not text:
        return []
    # Greenhouse commonly returns multiple offices separated by semicolons.
    # Keep slash-separated values intact because some cities legitimately contain '/'.
    return [part.strip() for part in text.split(";") if part.strip()]


def uid(): return int(get_jwt_identity())


def saved_payload(s):
    return {"id": s.id, "job": s.job.to_dict(), "status": s.status, "notes": s.notes or "", "created_at": s.created_at.isoformat(), "updated_at": s.updated_at.isoformat() if s.updated_at else None}


@jobs_bp.get("/api/jobs")
def get_jobs():
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(max(request.args.get("per_page", 20, type=int), 1), 50)
    search = request.args.get("search", "").strip()
    location = request.args.get("location", "").strip()
    job_type = request.args.get("job_type", "").strip()
    experience = request.args.get("experience", "").strip()
    company = request.args.get("company", "").strip()
    remote = request.args.get("remote", "false").lower() == "true"
    sort = request.args.get("sort", "relevant")
    query = Job.query.filter(Job.is_active.is_(True))
    if search:
        like = f"%{search}%"
        query = query.filter(or_(Job.title.ilike(like), Job.description.ilike(like), Company.name.ilike(like)))
    if location: query = query.filter(Job.location.ilike(f"%{location}%"))
    country = request.args.get("country", "").strip()
    if country:
        country_conditions = []
        for alias, canonical in COUNTRY_ALIASES.items():
            if canonical.lower() == country.lower():
                country_conditions.append(Job.location.ilike(f"%{alias}%"))
        country_conditions.append(Job.location.ilike(f"%{country}%"))
        query = query.filter(or_(*country_conditions))
    if job_type: query = query.filter(Job.job_type == job_type)
    if experience: query = query.filter(Job.experience_level == experience)
    if company: query = query.filter(Company.name.ilike(f"%{company}%"))
    if remote: query = query.filter(Job.remote.is_(True))
    query = query.join(Company)
    if sort == "newest": query = query.order_by(Job.posted_at.desc(), Job.scraped_at.desc())
    elif sort == "oldest": query = query.order_by(Job.posted_at.asc(), Job.scraped_at.asc())
    else: query = query.order_by(Job.posted_at.desc(), Job.scraped_at.desc(), Job.id.desc())
    p = query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({"jobs": [j.to_dict() for j in p.items], "total": p.total, "pages": p.pages, "current_page": p.page, "has_next": p.has_next, "has_prev": p.has_prev})


@jobs_bp.get("/api/locations")
def locations():
    """Return only locations that actually exist in the active job database.

    The frontend uses this for a country -> city/location cascading selector, so
    users never see hard-coded locations that have no matching jobs.
    """
    country_filter = request.args.get("country", "").strip().lower()
    grouped = {}
    rows = db.session.query(Job.location).filter(
        Job.is_active.is_(True), Job.location.isnot(None), Job.location != ""
    ).distinct().all()

    for (raw_location,) in rows:
        for location_value in split_locations(raw_location):
            country = extract_country(location_value) or "Other / Remote"
            if country_filter and country.lower() != country_filter:
                continue
            grouped.setdefault(country, set()).add(location_value)

    countries = [
        {"name": country, "locations": sorted(values, key=str.casefold)}
        for country, values in sorted(grouped.items(), key=lambda item: item[0].casefold())
    ]
    return jsonify({"countries": countries})


@jobs_bp.get("/api/jobs/<int:job_id>")
def get_job(job_id):
    job = db.session.get(Job, job_id)
    if not job: return jsonify({"message": "Job not found."}), 404
    return jsonify(job.to_dict(full=True))


@jobs_bp.post("/api/jobs/<int:job_id>/save")
@jwt_required()
def save_job(job_id):
    if not db.session.get(Job, job_id): return jsonify({"message": "Job not found."}), 404
    existing = SavedJob.query.filter_by(job_id=job_id, user_id=uid()).first()
    if existing: return jsonify({"message": "Job already saved", "saved_job": existing.id})
    saved = SavedJob(job_id=job_id, user_id=uid(), status="saved")
    db.session.add(saved); db.session.commit()
    return jsonify({"message": "Job saved", "saved_job": saved.id}), 201


@jobs_bp.post("/api/jobs/<int:job_id>/apply")
@jwt_required()
def apply_job(job_id):
    if not db.session.get(Job, job_id): return jsonify({"message": "Job not found."}), 404
    saved = SavedJob.query.filter_by(job_id=job_id, user_id=uid()).first()
    if saved: saved.status = "applied"
    else: saved = SavedJob(job_id=job_id, user_id=uid(), status="applied"); db.session.add(saved)
    db.session.commit()
    return jsonify({"message": "Application tracked", "saved_job": saved.id})


@jobs_bp.get("/api/saved")
@jwt_required()
def get_saved_jobs():
    return jsonify([saved_payload(s) for s in SavedJob.query.filter_by(user_id=uid()).order_by(SavedJob.updated_at.desc()).all()])


@jobs_bp.patch("/api/saved/<int:saved_id>")
@jwt_required()
def update_saved_job(saved_id):
    saved = SavedJob.query.filter_by(id=saved_id, user_id=uid()).first()
    if not saved: return jsonify({"message": "Saved job not found."}), 404
    data = request.get_json(silent=True) or {}
    if "status" in data:
        if data["status"] not in ALLOWED_STATUS: return jsonify({"message": "Invalid status."}), 400
        saved.status = data["status"]
    if "notes" in data: saved.notes = str(data["notes"])[:5000]
    db.session.commit(); return jsonify(saved_payload(saved))


@jobs_bp.delete("/api/saved/<int:saved_id>")
@jwt_required()
def delete_saved_job(saved_id):
    saved = SavedJob.query.filter_by(id=saved_id, user_id=uid()).first()
    if not saved: return jsonify({"message": "Saved job not found."}), 404
    db.session.delete(saved); db.session.commit(); return jsonify({"message": "Removed"})


@jobs_bp.get("/api/applications")
@jwt_required()
def applications():
    rows = SavedJob.query.filter(SavedJob.user_id == uid(), SavedJob.status != "saved").order_by(SavedJob.updated_at.desc()).all()
    return jsonify([saved_payload(s) for s in rows])


@jobs_bp.get("/api/companies")
def companies():
    search = request.args.get("search", "").strip()
    query = Company.query.outerjoin(Job).group_by(Company.id)
    if search: query = query.filter(Company.name.ilike(f"%{search}%"))
    rows = query.order_by(func.count(Job.id).desc(), Company.name.asc()).limit(100).all()
    return jsonify([dict(c.to_dict(), job_count=sum(1 for j in c.jobs if j.is_active)) for c in rows])


@jobs_bp.get("/api/companies/<int:company_id>")
def company_detail(company_id):
    c = db.session.get(Company, company_id)
    if not c: return jsonify({"message": "Company not found."}), 404
    jobs = Job.query.filter_by(company_id=company_id, is_active=True).order_by(Job.posted_at.desc()).limit(50).all()
    return jsonify({"company": c.to_dict(), "jobs": [j.to_dict() for j in jobs]})


@jobs_bp.get("/api/stats")
def get_stats():
    return jsonify({"total_jobs": Job.query.filter_by(is_active=True).count(), "total_companies": Company.query.count(), "remote_jobs": Job.query.filter_by(is_active=True, remote=True).count()})


@jobs_bp.get("/api/alerts")
@jwt_required()
def get_alerts(): return jsonify([a.to_dict() for a in JobAlert.query.filter_by(user_id=uid()).order_by(JobAlert.created_at.desc()).all()])


@jobs_bp.post("/api/alerts")
@jwt_required()
def create_alert():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "My Job Alert").strip()[:100]
    frequency = data.get("frequency", "daily")
    if frequency not in {"daily", "weekly", "instant"}: return jsonify({"message": "Invalid frequency."}), 400
    alert = JobAlert(user_id=uid(), name=name, keywords=str(data.get("keywords") or "")[:255], location=str(data.get("location") or "")[:180], job_type=data.get("job_type") or None, remote=bool(data.get("remote", False)), frequency=frequency)
    db.session.add(alert); db.session.commit(); return jsonify(alert.to_dict()), 201


@jobs_bp.patch("/api/alerts/<int:alert_id>")
@jwt_required()
def update_alert(alert_id):
    alert = JobAlert.query.filter_by(id=alert_id, user_id=uid()).first()
    if not alert: return jsonify({"message": "Alert not found."}), 404
    data = request.get_json(silent=True) or {}
    for field, maxlen in (("name",100),("keywords",255),("location",180)):
        if field in data: setattr(alert, field, str(data[field])[:maxlen])
    if "job_type" in data: alert.job_type = data["job_type"] or None
    if "remote" in data: alert.remote = bool(data["remote"])
    if "is_active" in data: alert.is_active = bool(data["is_active"])
    if "frequency" in data and data["frequency"] in {"daily","weekly","instant"}: alert.frequency = data["frequency"]
    db.session.commit(); return jsonify(alert.to_dict())


@jobs_bp.delete("/api/alerts/<int:alert_id>")
@jwt_required()
def delete_alert(alert_id):
    alert = JobAlert.query.filter_by(id=alert_id, user_id=uid()).first()
    if not alert: return jsonify({"message": "Alert not found."}), 404
    db.session.delete(alert); db.session.commit(); return jsonify({"message": "Alert deleted"})
