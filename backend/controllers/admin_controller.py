from flask import Blueprint, jsonify, request
from controllers.middleware import admin_required
from database import get_db
from models import STATUT_DEMANDE_EN_ATTENTE, User
from services.admin_service import AdminService


admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


@admin_bp.route("/recruiter-requests", methods=["GET"])
@admin_required
def list_recruiter_requests(current_user):
    db = get_db()
    try:
        users = db.query(User).filter_by(statut_demande_recruteur=STATUT_DEMANDE_EN_ATTENTE).all()
        return jsonify({
            "requests": [
                {
                    "id": user.id,
                    "nom": user.nom,
                    "email": user.email,
                    "role": user.role,
                    "statut_demande_recruteur": user.statut_demande_recruteur,
                    "entreprise_demande_recruteur": user.entreprise_demande_recruteur,
                    "referent_rh_demande_recruteur": user.referent_rh_demande_recruteur,
                }
                for user in users
            ]
        })
    finally:
        db.close()


@admin_bp.route("/users/<int:user_id>/grant-recruiter", methods=["POST"])
@admin_required
def grant_recruiter(current_user, user_id):
    data = request.get_json() or {}
    db = get_db()
    try:
        user = AdminService(db).grant_recruiter_role(user_id, data.get("entreprise", ""))
        return jsonify({"user": user})
    except ValueError as error:
        db.rollback()
        return jsonify({"error": str(error)}), 400
    finally:
        db.close()
