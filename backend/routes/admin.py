from flask import Blueprint, jsonify, request
from sqlalchemy import func, or_
from werkzeug.security import generate_password_hash
from models import db, User, Job, Company, SavedJob
from flask_jwt_extended import get_jwt_identity
from auth import admin_required

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')


def user_payload(user):
    return {
        'id': user.id, 'name': user.name, 'email': user.email, 'role': user.role,
        'is_active': user.is_active, 'created_at': user.created_at.isoformat() if user.created_at else None
    }


@admin_bp.get('/dashboard')
@admin_required
def dashboard():
    return jsonify({
        'users': User.query.count(),
        'active_users': User.query.filter_by(is_active=True).count(),
        'admins': User.query.filter_by(role='admin').count(),
        'jobs': Job.query.count(),
        'active_jobs': Job.query.filter_by(is_active=True).count(),
        'companies': Company.query.count(),
        'saved_jobs': SavedJob.query.count(),
        'applications': SavedJob.query.filter(SavedJob.status != 'saved').count(),
    })


@admin_bp.get('/users')
@admin_required
def users():
    search = request.args.get('search', '').strip()
    query = User.query
    if search:
        like = f'%{search}%'
        query = query.filter(or_(User.name.ilike(like), User.email.ilike(like)))
    rows = query.order_by(User.created_at.desc()).all()
    return jsonify([user_payload(u) for u in rows])


@admin_bp.patch('/users/<int:user_id>')
@admin_required
def update_user(user_id):
    user = db.session.get(User, user_id)
    if not user:
        return jsonify({'message': 'User not found.'}), 404
    data = request.get_json(silent=True) or {}
    if 'is_active' in data:
        current_id = int(get_jwt_identity())
        if user.id == current_id and not bool(data['is_active']):
            return jsonify({'message': 'You cannot disable your own admin account.'}), 400
        user.is_active = bool(data['is_active'])
    if 'role' in data and data['role'] in {'user', 'admin'}:
        user.role = data['role']
    db.session.commit()
    return jsonify(user_payload(user))


@admin_bp.get('/jobs')
@admin_required
def jobs():
    search = request.args.get('search', '').strip()
    query = Job.query.join(Company)
    if search:
        like = f'%{search}%'
        query = query.filter(or_(Job.title.ilike(like), Company.name.ilike(like)))
    rows = query.order_by(Job.scraped_at.desc()).limit(200).all()
    return jsonify([j.to_dict() for j in rows])


@admin_bp.patch('/jobs/<int:job_id>')
@admin_required
def update_job(job_id):
    job = db.session.get(Job, job_id)
    if not job:
        return jsonify({'message': 'Job not found.'}), 404
    data = request.get_json(silent=True) or {}
    if 'is_active' in data:
        job.is_active = bool(data['is_active'])
    db.session.commit()
    return jsonify(job.to_dict())


@admin_bp.get('/companies')
@admin_required
def admin_companies():
    rows = Company.query.order_by(Company.name.asc()).all()
    return jsonify([dict(c.to_dict(), job_count=sum(1 for j in c.jobs if j.is_active)) for c in rows])
