import os, uuid
from flask import Blueprint, jsonify, request, send_from_directory, current_app
from flask_jwt_extended import get_jwt_identity, jwt_required
from models import User, Resume, db

profile_bp = Blueprint("profile", __name__, url_prefix="/api")
ALLOWED_EXT = {"pdf"}

def user(): return db.session.get(User, int(get_jwt_identity()))

def payload(u):
    return {"id":u.id,"name":u.name,"email":u.email,"role":u.role,"phone":u.phone,"headline":u.headline,"location":u.location,"skills":u.skills or "","bio":u.bio or "","created_at":u.created_at.isoformat()}

@profile_bp.get("/profile")
@jwt_required()
def get_profile(): return jsonify({"user": payload(user())})

@profile_bp.patch("/profile")
@jwt_required()
def update_profile():
    u=user(); data=request.get_json(silent=True) or {}
    for field, limit in (("name",120),("phone",30),("headline",180),("location",180),("skills",2000),("bio",5000)):
        if field in data: setattr(u, field, str(data[field]).strip()[:limit])
    db.session.commit(); return jsonify({"user":payload(u)})

@profile_bp.get("/resumes")
@jwt_required()
def resumes(): return jsonify([r.to_dict() for r in Resume.query.filter_by(user_id=user().id).order_by(Resume.created_at.desc()).all()])

@profile_bp.post("/resumes")
@jwt_required()
def upload_resume():
    file=request.files.get("resume")
    if not file or not file.filename: return jsonify({"message":"Choose a PDF resume."}),400
    ext=file.filename.rsplit('.',1)[-1].lower() if '.' in file.filename else ''
    if ext not in ALLOWED_EXT or file.mimetype != 'application/pdf': return jsonify({"message":"Only PDF resumes are allowed."}),400
    upload_dir=os.path.join(current_app.instance_path,"resumes",str(user().id)); os.makedirs(upload_dir,exist_ok=True)
    stored=f"{uuid.uuid4().hex}.pdf"; path=os.path.join(upload_dir,stored); file.save(path)
    size=os.path.getsize(path)
    if size > current_app.config["MAX_CONTENT_LENGTH"]: os.remove(path); return jsonify({"message":"Resume is too large."}),413
    Resume.query.filter_by(user_id=user().id).update({"is_primary":False})
    r=Resume(user_id=user().id,filename=os.path.basename(file.filename)[:255],stored_name=stored,content_type=file.mimetype,size_bytes=size,is_primary=True)
    db.session.add(r); db.session.commit(); return jsonify(r.to_dict()),201

@profile_bp.get("/resumes/<int:resume_id>/download")
@jwt_required()
def download_resume(resume_id):
    r=Resume.query.filter_by(id=resume_id,user_id=user().id).first()
    if not r: return jsonify({"message":"Resume not found."}),404
    return send_from_directory(os.path.join(current_app.instance_path,"resumes",str(user().id)),r.stored_name,as_attachment=True,download_name=r.filename)

@profile_bp.delete("/resumes/<int:resume_id>")
@jwt_required()
def delete_resume(resume_id):
    r=Resume.query.filter_by(id=resume_id,user_id=user().id).first()
    if not r: return jsonify({"message":"Resume not found."}),404
    path=os.path.join(current_app.instance_path,"resumes",str(user().id),r.stored_name)
    if os.path.exists(path): os.remove(path)
    db.session.delete(r); db.session.commit(); return jsonify({"message":"Resume deleted"})
