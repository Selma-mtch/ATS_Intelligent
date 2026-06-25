from flask import Blueprint, current_app, jsonify, request

from controllers.middleware import login_required
from database import get_db
from services.cv_service import CVService
from services.matching_service import MatchingService


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
    if not current_user.candidat or not current_user.candidat.cv:
        return jsonify({"cv": None})

    cv = current_user.candidat.cv
    return jsonify({
        "cv": {
            "id": cv.id,
            "fichier_pdf": cv.fichier_pdf,
            "texte_extrait": cv.texte_extrait,
            "chunks": [
                {
                    "id": chunk.id,
                    "type_section": chunk.type_section,
                    "contenu": chunk.contenu,
                }
                for chunk in cv.chunks
            ],
        }
    })

@cv_bp.route("/matching-offers", methods=["GET"])
@login_required
def get_my_matching_offers(current_user):
    """Trouve les offres adaptées au CV du candidat connecté."""
    db = get_db()
    try:
        # On vérifie si le candidat a un CV
        if not current_user.cv:
            return jsonify({"error": "Veuillez d'abord uploader votre CV au format PDF"}), 400
            
        matcher = MatchingService(db)
        recommendations = matcher.get_recommended_offers(current_user.cv.chunks)
        
        return jsonify({"offres": recommendations}), 200
    finally:
        db.close()
