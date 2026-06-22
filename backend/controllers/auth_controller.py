from flask import Blueprint, jsonify, request, session
from database import get_db
from services.auth_service import AuthService
from controllers.middleware import login_required


auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    db = get_db()
    try:
        user = AuthService(db).register(
            data.get("nom", ""),
            data.get("email", ""),
            data.get("mot_de_passe", ""),
        )
        session["user_id"] = user["id"]
        return jsonify({"user": user}), 201
    except ValueError as error:
        db.rollback()
        return jsonify({"error": str(error)}), 400
    finally:
        db.close()


@auth_bp.route("/request-recruiter-role", methods=["POST"])
@login_required
def request_recruiter_role(current_user):
    data = request.get_json() or {}
    db = get_db()
    try:
        user = AuthService(db).request_recruiter_role(
            current_user.id,
            data.get("entreprise", ""),
            data.get("referent_rh", ""),
        )
        return jsonify({"user": user})
    except ValueError as error:
        db.rollback()
        return jsonify({"error": str(error)}), 400
    finally:
        db.close()


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json() or {}
    db = get_db()
    try:
        user = AuthService(db).login(
            data.get("email", ""),
            data.get("mot_de_passe", ""),
        )
        session["user_id"] = user["id"]
        return jsonify({"user": user})
    except ValueError as error:
        return jsonify({"error": str(error)}), 400
    except PermissionError as error:
        return jsonify({"error": str(error)}), 401
    finally:
        db.close()


@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"message": "Deconnecte avec succes"})


@auth_bp.route("/me", methods=["GET"])
@login_required
def me(current_user):
    return jsonify({
        "user": {
            "id": current_user.id,
            "nom": current_user.nom,
            "email": current_user.email,
            "role": current_user.role,
            "demande_role_recruteur": current_user.demande_role_recruteur,
            "statut_demande_recruteur": current_user.statut_demande_recruteur,
            "entreprise_demande_recruteur": current_user.entreprise_demande_recruteur,
            "referent_rh_demande_recruteur": current_user.referent_rh_demande_recruteur,
        }
    })
