from flask import Blueprint, current_app, jsonify, request

from controllers.middleware import login_required
from database import get_db
from services.cv_service import CVService


cv_bp = Blueprint("cv", __name__, url_prefix="/cv")


@cv_bp.route("/upload", methods=["POST"])
@login_required
def upload_cv(current_user):
    if current_user.role != "candidat":
        return jsonify({"error": "Seul un candidat peut deposer un CV"}), 403
    if not current_user.candidat:
        return jsonify({"error": "Profil candidat introuvable"}), 400

    uploaded_file = request.files.get("cv")
    db = get_db()
    try:
        result = CVService(db).upload_cv(current_user.candidat.id, uploaded_file)
        return jsonify(result), 201
    except ValueError as error:
        db.rollback()
        return jsonify({"error": str(error)}), 400
    except Exception:
        current_app.logger.exception("Erreur inattendue pendant le traitement du CV")
        db.rollback()
        return jsonify({"error": "Erreur pendant le traitement du CV"}), 500
    finally:
        db.close()


@cv_bp.route("/me", methods=["GET"])
@login_required
def get_my_cv(current_user):
    if current_user.role != "candidat":
        return jsonify({"error": "Seul un candidat peut consulter son CV"}), 403
    if not current_user.candidat:
        return jsonify({"cvs": [], "cv_selectionne": None})

    db = get_db()
    try:
        cvs = CVService(db).list_cvs(current_user.candidat.id)
        selected_cv = next((cv for cv in cvs if cv["est_selectionne"] == "oui"), None)
        return jsonify({"cvs": cvs, "cv_selectionne": selected_cv, "cv": selected_cv})
    finally:
        db.close()


@cv_bp.route("/<int:cv_id>/select", methods=["POST"])
@login_required
def select_cv(current_user, cv_id):
    if current_user.role != "candidat":
        return jsonify({"error": "Seul un candidat peut selectionner un CV"}), 403
    if not current_user.candidat:
        return jsonify({"error": "Profil candidat introuvable"}), 400

    db = get_db()
    try:
        cv = CVService(db).select_cv(current_user.candidat.id, cv_id)
        return jsonify({"cv": cv})
    except ValueError as error:
        db.rollback()
        return jsonify({"error": str(error)}), 400
    finally:
        db.close()


@cv_bp.route("/<int:cv_id>", methods=["DELETE"])
@login_required
def delete_cv(current_user, cv_id):
    if current_user.role != "candidat":
        return jsonify({"error": "Seul un candidat peut supprimer un CV"}), 403
    if not current_user.candidat:
        return jsonify({"error": "Profil candidat introuvable"}), 400

    db = get_db()
    try:
        CVService(db).delete_cv(current_user.candidat.id, cv_id)
        return jsonify({"message": "CV supprime"})
    except ValueError as error:
        db.rollback()
        return jsonify({"error": str(error)}), 400
    finally:
        db.close()
