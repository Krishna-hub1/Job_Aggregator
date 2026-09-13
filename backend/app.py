import os, threading, logging
from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required
from sqlalchemy import inspect, text
from config import Config
from models import db, Job, Company, User
from routes.jobs import jobs_bp
from routes.admin import admin_bp
from routes.profile import profile_bp
from auth import auth_bp, admin_required

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger=logging.getLogger("jobhub")

def ensure_schema():
    inspector=inspect(db.engine); tables=inspector.get_table_names()
    # Add columns used by upgraded versions. New tables are handled by create_all.
    migrations={
      "users": {"role":"VARCHAR(20) NOT NULL DEFAULT 'user'","is_active":"BOOLEAN NOT NULL DEFAULT TRUE","phone":"VARCHAR(30) NULL","headline":"VARCHAR(180) NULL","location":"VARCHAR(180) NULL","skills":"TEXT NULL","bio":"TEXT NULL","updated_at":"DATETIME NULL"},
      "jobs": {"external_id":"VARCHAR(255) NULL","apply_url":"VARCHAR(1000) NOT NULL"},
      "saved_jobs": {"user_id":"INTEGER NULL","updated_at":"DATETIME NULL"},
    }
    for table, cols in migrations.items():
        if table not in tables: continue
        existing={c['name'] for c in inspector.get_columns(table)}
        for name, definition in cols.items():
            if name not in existing:
                db.session.execute(text(f"ALTER TABLE {table} ADD COLUMN {name} {definition}"))
    db.session.commit()


def create_app():
    app=Flask(__name__, instance_relative_config=True); app.config.from_object(Config); os.makedirs(app.instance_path,exist_ok=True)
    if not app.config.get("JWT_SECRET_KEY") or app.config["JWT_SECRET_KEY"]=="change-this-secret-in-production":
        if os.getenv("FLASK_ENV") == "production": raise RuntimeError("JWT_SECRET_KEY must be set in production")
        app.config["JWT_SECRET_KEY"]="dev-only-change-me"
    CORS(app, resources={r"/api/*":{"origins":os.getenv("CORS_ORIGINS","http://localhost:5173").split(',')}})
    JWTManager(app); db.init_app(app)
    app.register_blueprint(auth_bp); app.register_blueprint(jobs_bp); app.register_blueprint(profile_bp); app.register_blueprint(admin_bp)
    @app.errorhandler(404)
    def not_found(_): return jsonify({"message":"Resource not found."}),404
    @app.errorhandler(413)
    def too_large(_): return jsonify({"message":"Uploaded file is too large."}),413
    @app.errorhandler(500)
    def server_error(exc):
        db.session.rollback(); logger.exception("Unhandled server error",exc_info=exc); return jsonify({"message":"Internal server error."}),500
    @app.after_request
    def security_headers(response):
        response.headers["X-Content-Type-Options"]="nosniff"
        response.headers["X-Frame-Options"]="DENY"
        response.headers["Referrer-Policy"]="strict-origin-when-cross-origin"
        return response
    with app.app_context():
        db.create_all(); ensure_schema()
        # Create/update the configured admin account without exposing admin signup.
        admin_email = os.getenv("ADMIN_EMAIL", "").strip().lower()
        admin_password = os.getenv("ADMIN_PASSWORD", "").strip()
        if admin_email and admin_password:
            from werkzeug.security import generate_password_hash
            admin = User.query.filter_by(email=admin_email).first()
            if not admin:
                admin = User(name=os.getenv("ADMIN_NAME", "JobHub Admin"), email=admin_email, password_hash=generate_password_hash(admin_password), role="admin")
                db.session.add(admin)
            else:
                admin.role = "admin"; admin.is_active = True
            db.session.commit()
    return app

app=create_app(); _scrape_lock=threading.Lock(); _last_scrape_summary=None

def scheduled_scrape():
    global _last_scrape_summary
    if not _scrape_lock.acquire(False): return {"message":"Scrape already running"}
    try:
        with app.app_context():
            from scrapers.runner import run_scrapers
            _last_scrape_summary=run_scrapers(); return _last_scrape_summary
    except Exception as exc:
        logger.exception("Scrape failed"); return {"error":str(exc)}
    finally: _scrape_lock.release()

def initial_scrape_if_empty():
    with app.app_context():
        if Job.query.count()==0 and os.getenv("SCRAPE_ON_START","true").lower()=="true": return scheduled_scrape()

def start_scheduler():
    scheduler=BackgroundScheduler(timezone=os.getenv("APP_TIMEZONE","Asia/Kolkata"))
    scheduler.add_job(initial_scrape_if_empty,"date",id="initial_scrape",replace_existing=True)
    scheduler.add_job(scheduled_scrape,"interval",hours=max(int(os.getenv("SCRAPE_INTERVAL_HOURS","24")),1),id="daily_scrape",replace_existing=True)
    scheduler.start(); return scheduler

@app.get("/")
def root(): return {"message":"JobHub API is running","docs":"Use /api/health"}

@app.get("/api/health")
def health():
    try:
        with app.app_context(): return {"status":"ok","database":"connected","jobs":Job.query.count(),"companies":Company.query.count(),"last_scrape":_last_scrape_summary}
    except Exception: return {"status":"error","database":"unavailable"},503

@app.post("/api/scrape")
@admin_required
def trigger_scrape():
    # Keep manual scraping protected by auth; deployment should also gate this behind an admin proxy.
    summary=scheduled_scrape(); return summary, 200 if "error" not in summary else 500

if __name__=="__main__":
    scheduler=start_scheduler()
    try: app.run(host=os.getenv("HOST","127.0.0.1"),port=int(os.getenv("PORT","5000")),debug=False,use_reloader=False)
    finally: scheduler.shutdown(wait=False)
