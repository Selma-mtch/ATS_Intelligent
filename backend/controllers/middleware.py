from functools import wraps
from flask import jsonify, session
from database import get_db
from models import ROLE_ADMINISTRATEUR, User


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Connexion requise"}), 401

        db = get_db()
        try:
            user = db.get(User, user_id)
            if not user:
                session.clear()
                return jsonify({"error": "Session invalide"}), 401
            return view(user, *args, **kwargs)
        finally:
            db.close()

    return wrapped


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Connexion requise"}), 401

        db = get_db()
        try:
            user = db.get(User, user_id)
            if not user:
                session.clear()
                return jsonify({"error": "Session invalide"}), 401
            if user.role != ROLE_ADMINISTRATEUR:
                return jsonify({"error": "Droits administrateur requis"}), 403
            return view(user, *args, **kwargs)
        finally:
            db.close()

    return wrapped


def recruiter_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify({"error": "Connexion requise"}), 401

        db = get_db()
        try:
            user = db.get(User, user_id)
            if not user:
                session.clear()
                return jsonify({"error": "Session invalide"}), 401
            if user.role not in (ROLE_ADMINISTRATEUR, "recruteur"):
                return jsonify({"error": "Droits recruteur requis"}), 403
            return view(user, *args, **kwargs)
        finally:
            db.close()

    return wrapped
