from flask import Blueprint, jsonify, request
from controllers.middleware import login_required, recruiter_required
from database import get_db
from services.offre_service import OffreService


offre_bp = Blueprint("offre", __name__, url_prefix="/offres")


@offre_bp.route("", methods=["POST"])
@recruiter_required
def create_offre(current_user):
    data = request.get_json() or {}
    db = get_db()
    try:
        offre = OffreService(db).create(
            current_user,
            data.get("titre", ""),
            data.get("description", ""),
            data.get("competences", ""),
        )
        return jsonify({"offre": offre}), 201
    except ValueError as error:
        db.rollback()
        return jsonify({"error": str(error)}), 400
    finally:
        db.close()


@offre_bp.route("", methods=["GET"])
def list_offres():
    db = get_db()
    try:
        offres = OffreService(db).list_all()
        return jsonify({"offres": offres})
    finally:
        db.close()


@offre_bp.route("/mes-offres", methods=["GET"])
@recruiter_required
def mes_offres(current_user):
    db = get_db()
    try:
        offres = OffreService(db).list_by_recruteur(current_user)
        return jsonify({"offres": offres})
    finally:
        db.close()


@offre_bp.route("/<int:offre_id>", methods=["GET"])
def get_offre(offre_id):
    db = get_db()
    try:
        offre = OffreService(db).get(offre_id)
        return jsonify({"offre": offre})
    except ValueError as error:
        return jsonify({"error": str(error)}), 404
    finally:
        db.close()


@offre_bp.route("/<int:offre_id>", methods=["DELETE"])
@recruiter_required
def delete_offre(current_user, offre_id):
    db = get_db()
    try:
        OffreService(db).delete(current_user, offre_id)
        return jsonify({"message": "Offre supprimee"})
    except ValueError as error:
        return jsonify({"error": str(error)}), 404
    except PermissionError as error:
        return jsonify({"error": str(error)}), 403
    finally:
        db.close()
