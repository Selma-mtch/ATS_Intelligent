from flask import Blueprint, current_app, jsonify, request

from controllers.middleware import recruiter_required
from database import get_db
from services.offre_service import OffreService


offre_bp = Blueprint("offre", __name__, url_prefix="/offres")


@offre_bp.route("", methods=["POST"])
@recruiter_required
def create_offre(current_user):
    recruteur_id = current_user.recruteur.id
    data = request.get_json() or {}
    db = get_db()
    try:
        offre = OffreService(db).create_offre(recruteur_id, data)
        return jsonify({"offre": offre}), 201
    except ValueError as error:
        db.rollback()
        return jsonify({"error": str(error)}), 400
    except Exception:
        current_app.logger.exception("Erreur inattendue pendant la creation d'offre")
        db.rollback()
        return jsonify({"error": "Erreur pendant la creation de l'offre"}), 500
    finally:
        db.close()


@offre_bp.route("/mine", methods=["GET"])
@recruiter_required
def list_my_offres(current_user):
    recruteur_id = current_user.recruteur.id
    db = get_db()
    try:
        offres = OffreService(db).list_mes_offres(recruteur_id)
        return jsonify({"offres": offres})
    finally:
        db.close()
