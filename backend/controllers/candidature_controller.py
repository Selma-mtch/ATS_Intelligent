from flask import Blueprint, jsonify, request
from controllers.middleware import login_required, recruiter_required
from database import get_db
from services.candidature_service import CandidatureService


candidature_bp = Blueprint("candidature", __name__, url_prefix="/candidatures")


@candidature_bp.route("", methods=["POST"])
@login_required
def postuler(current_user):
    data = request.get_json() or {}
    db = get_db()
    try:
        candidature = CandidatureService(db).postuler(
            current_user,
            data.get("offre_id"),
        )
        return jsonify({"candidature": candidature}), 201
    except ValueError as error:
        db.rollback()
        return jsonify({"error": str(error)}), 400
    finally:
        db.close()


@candidature_bp.route("", methods=["GET"])
@login_required
def mes_candidatures(current_user):
    db = get_db()
    try:
        candidatures = CandidatureService(db).list_by_candidat(current_user)
        return jsonify({"candidatures": candidatures})
    finally:
        db.close()


@candidature_bp.route("/offre/<int:offre_id>", methods=["GET"])
@recruiter_required
def candidatures_par_offre(current_user, offre_id):
    db = get_db()
    try:
        candidatures = CandidatureService(db).list_by_offre(current_user, offre_id)
        return jsonify({"candidatures": candidatures})
    except ValueError as error:
        return jsonify({"error": str(error)}), 404
    except PermissionError as error:
        return jsonify({"error": str(error)}), 403
    finally:
        db.close()


@candidature_bp.route("/<int:candidature_id>/statut", methods=["PUT"])
@recruiter_required
def update_statut(current_user, candidature_id):
    data = request.get_json() or {}
    db = get_db()
    try:
        candidature = CandidatureService(db).update_statut(
            current_user,
            candidature_id,
            data.get("statut", ""),
        )
        return jsonify({"candidature": candidature})
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except PermissionError as error:
        return jsonify({"error": str(error)}), 403
    finally:
        db.close()
