from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    phone = db.Column(db.String(30))
    headline = db.Column(db.String(180))
    location = db.Column(db.String(180))
    skills = db.Column(db.Text)
    bio = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    saved_jobs = db.relationship("SavedJob", backref="user", lazy=True, cascade="all, delete-orphan")
    alerts = db.relationship("JobAlert", backref="user", lazy=True, cascade="all, delete-orphan")
    resumes = db.relationship("Resume", backref="user", lazy=True, cascade="all, delete-orphan")


class Company(db.Model):
    __tablename__ = "companies"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    website = db.Column(db.String(500))
    logo_url = db.Column(db.String(1000))
    ats_platform = db.Column(db.String(30))
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    jobs = db.relationship("Job", backref="company", lazy=True)
    __table_args__ = (db.UniqueConstraint("name", "ats_platform", name="unique_company"),)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "website": self.website, "logo_url": self.logo_url, "ats_platform": self.ats_platform}


class Job(db.Model):
    __tablename__ = "jobs"
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey("companies.id"), nullable=False, index=True)
    external_id = db.Column(db.String(255), index=True)
    title = db.Column(db.String(255), nullable=False, index=True)
    location = db.Column(db.String(255), index=True)
    job_type = db.Column(db.String(30))
    experience_level = db.Column(db.String(30))
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    description = db.Column(db.Text)
    apply_url = db.Column(db.String(1000), nullable=False)
    remote = db.Column(db.Boolean, default=False, nullable=False, index=True)
    posted_at = db.Column(db.Date)
    scraped_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    __table_args__ = (db.UniqueConstraint("company_id", "apply_url", name="unique_job"),)

    def to_dict(self, full=False):
        description = self.description or ""
        return {
            "id": self.id,
            "title": self.title,
            "company": self.company.to_dict(),
            "location": self.location,
            "job_type": self.job_type,
            "experience_level": self.experience_level,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "description": description if full else description[:500],
            "apply_url": self.apply_url,
            "remote": self.remote,
            "posted_at": self.posted_at.isoformat() if self.posted_at else None,
            "scraped_at": self.scraped_at.isoformat() if self.scraped_at else None,
            "is_active": self.is_active,
        }


class SavedJob(db.Model):
    __tablename__ = "saved_jobs"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True, index=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False, index=True)
    status = db.Column(db.String(20), default="saved", nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    job = db.relationship("Job", backref="saved_entries")
    __table_args__ = (db.UniqueConstraint("user_id", "job_id", name="unique_user_saved_job"),)


class JobAlert(db.Model):
    __tablename__ = "job_alerts"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    keywords = db.Column(db.String(255))
    location = db.Column(db.String(180))
    job_type = db.Column(db.String(30))
    remote = db.Column(db.Boolean, default=False, nullable=False)
    frequency = db.Column(db.String(20), default="daily", nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "keywords": self.keywords, "location": self.location, "job_type": self.job_type, "remote": self.remote, "frequency": self.frequency, "is_active": self.is_active, "created_at": self.created_at.isoformat()}


class Resume(db.Model):
    __tablename__ = "resumes"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    stored_name = db.Column(db.String(255), nullable=False, unique=True)
    content_type = db.Column(db.String(100))
    size_bytes = db.Column(db.Integer)
    is_primary = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {"id": self.id, "filename": self.filename, "content_type": self.content_type, "size_bytes": self.size_bytes, "is_primary": self.is_primary, "created_at": self.created_at.isoformat()}
