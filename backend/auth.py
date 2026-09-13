import os
import re
from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from werkzeug.security import check_password_hash, generate_password_hash
from models import User, db

auth_bp = Blueprint("auth", __name__, url_prefix="/api/auth")
EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


def user_payload(user):
    return {"id": user.id, "name": user.name, "email": user.email, "role": user.role, "is_active": user.is_active, "phone": user.phone, "headline": user.headline, "location": user.location, "skills": user.skills or "", "bio": user.bio or "", "created_at": user.created_at.isoformat() if user.created_at else None}


def issue_token(user):
    return create_access_token(identity=str(user.id), additional_claims={"role": user.role})


def current_user():
    user_id = int(get_jwt_identity())
    return db.session.get(User, user_id)


@auth_bp.post("/register")
def register():
    data = request.get_json(silent=True) or {}
    name, email, password = (data.get("name") or "").strip(), (data.get("email") or "").strip().lower(), data.get("password") or ""
    if len(name) < 2: return jsonify({"message": "Please enter your name."}), 400
    if not EMAIL_RE.match(email): return jsonify({"message": "Please enter a valid email address."}), 400
    if len(password) < 8: return jsonify({"message": "Password must be at least 8 characters."}), 400
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password): return jsonify({"message": "Password must contain letters and numbers."}), 400
    if User.query.filter_by(email=email).first(): return jsonify({"message": "An account with this email already exists."}), 409
    user = User(name=name, email=email, password_hash=generate_password_hash(password), role="user")
    db.session.add(user); db.session.commit()
    return jsonify({"token": issue_token(user), "user": user_payload(user)}), 201


@auth_bp.post("/login")
def login():
    data = request.get_json(silent=True) or {}
    email, password = (data.get("email") or "").strip().lower(), data.get("password") or ""
    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password): return jsonify({"message": "Invalid email or password."}), 401
    if not user.is_active: return jsonify({"message": "Your account has been disabled by an administrator."}), 403
    return jsonify({"token": issue_token(user), "user": user_payload(user)})


@auth_bp.get("/me")
@jwt_required()
def me():
    user = current_user()
    if not user: return jsonify({"message": "User not found."}), 404
    return jsonify({"user": user_payload(user)})


def admin_required(fn):
    from functools import wraps
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = current_user()
        if not user or user.role != "admin":
            return jsonify({"message": "Admin access required."}), 403
        return fn(*args, **kwargs)
    return wrapper


@auth_bp.post("/change-password")
@jwt_required()
def change_password():
    user = current_user(); data = request.get_json(silent=True) or {}
    old = data.get("current_password") or ""; new = data.get("new_password") or ""
    if not check_password_hash(user.password_hash, old): return jsonify({"message":"Current password is incorrect."}), 400
    if len(new) < 8 or not re.search(r"[A-Za-z]", new) or not re.search(r"\d", new): return jsonify({"message":"New password must be 8+ characters and contain letters and numbers."}), 400
    user.password_hash = generate_password_hash(new); db.session.commit(); return jsonify({"message":"Password changed successfully."})
