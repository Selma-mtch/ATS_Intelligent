from flask import Blueprint, jsonify, request
from controllers.middleware import login_required
from database import get_db
from services.cv_service import CVService


cv_bp = Blueprint("cv", __name__, url_prefix="/cv")


@cv_bp.route("/upload", methods=["POST"])
@login_required
def upload_cv(current_user):
    db = get_db()
    try:
        file = request.files.get("fichier")
        cv = CVService(db).upload(current_user, file)
        return jsonify({"cv": cv}), 201
    except ValueError as error:
        db.rollback()
        return jsonify({"error": str(error)}), 400
    finally:
        db.close()


@cv_bp.route("", methods=["GET"])
@login_required
def get_cv(current_user):
    db = get_db()
    try:
        cv = CVService(db).get(current_user)
        if not cv:
            return jsonify({"cv": None, "message": "Aucun CV depose"})
        return jsonify({"cv": cv})
    finally:
        db.close()
