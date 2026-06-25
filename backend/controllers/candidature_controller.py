from flask import Blueprint, jsonify, request

from controllers.middleware import login_required
from database import get_db
from models import ROLE_CANDIDAT, ROLE_RECRUTEUR, Offre
from services.candidature_service import CandidatureService


candidature_bp = Blueprint("candidature", __name__, url_prefix="/candidatures")


@candidature_bp.route("", methods=["POST"])
@login_required
def postuler(current_user):
    if current_user.role != ROLE_CANDIDAT or not current_user.candidat:
        return jsonify({"error": "Seul un candidat peut postuler"}), 403

    data = request.get_json() or {}
    db = get_db()
    try:
        candidature = CandidatureService(db).postuler(
            current_user.candidat.id, data.get("offre_id")
        )
        return jsonify({"candidature": candidature}), 201
    except ValueError as error:
        db.rollback()
        return jsonify({"error": str(error)}), 400
    finally:
        db.close()


@candidature_bp.route("/mine", methods=["GET"])
@login_required
def mes_candidatures(current_user):
    if current_user.role != ROLE_CANDIDAT or not current_user.candidat:
        return jsonify({"error": "Seul un candidat peut consulter ses candidatures"}), 403

    db = get_db()
    try:
        return jsonify(
            {"candidatures": CandidatureService(db).list_mes_candidatures(current_user.candidat.id)}
        )
    finally:
        db.close()


@candidature_bp.route("/offre/<int:offre_id>", methods=["GET"])
@login_required
def candidats_offre(current_user, offre_id):
    if current_user.role != ROLE_RECRUTEUR or not current_user.recruteur:
        return jsonify({"error": "Droits recruteur requis"}), 403

    db = get_db()
    try:
        offre = db.get(Offre, offre_id)
        if not offre:
            return jsonify({"error": "Offre introuvable"}), 404
        if offre.recruteur_id != current_user.recruteur.id:
            return jsonify({"error": "Cette offre ne vous appartient pas"}), 403
        return jsonify({"candidatures": CandidatureService(db).list_candidats_offre(offre_id)})
    finally:
        db.close()


@candidature_bp.route("/<int:candidature_id>/cv", methods=["GET"])
@login_required
def cv_candidature(current_user, candidature_id):
    if current_user.role != ROLE_RECRUTEUR or not current_user.recruteur:
        return jsonify({"error": "Droits recruteur requis"}), 403

    db = get_db()
    try:
        cv = CandidatureService(db).get_cv_candidature(current_user.recruteur.id, candidature_id)
        return jsonify({"cv": cv})
    except PermissionError as error:
        return jsonify({"error": str(error)}), 403
    except ValueError as error:
        return jsonify({"error": str(error)}), 404
    finally:
        db.close()


@candidature_bp.route("/<int:candidature_id>/statut", methods=["POST"])
@login_required
def changer_statut(current_user, candidature_id):
    if current_user.role != ROLE_RECRUTEUR or not current_user.recruteur:
        return jsonify({"error": "Droits recruteur requis"}), 403

    data = request.get_json() or {}
    db = get_db()
    try:
        candidature = CandidatureService(db).changer_statut(
            current_user.recruteur.id, candidature_id, data.get("statut")
        )
        return jsonify({"candidature": candidature})
    except PermissionError as error:
        db.rollback()
        return jsonify({"error": str(error)}), 403
    except ValueError as error:
        db.rollback()
        return jsonify({"error": str(error)}), 400
    finally:
        db.close()
