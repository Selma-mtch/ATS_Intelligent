import bcrypt
from repositories.user_repository import UserRepository
from utils import user_to_dict


class AuthService:
    def __init__(self, db):
        self.db = db
        self.users = UserRepository(db)

    def register(self, nom: str, email: str, password: str):
        nom = (nom or "").strip()
        email = (email or "").strip().lower()

        if not nom or not email:
            raise ValueError("Nom et email requis")
        if not password:
            raise ValueError("Mot de passe requis")
        if len(password) < 6:
            raise ValueError("Mot de passe trop court")
        if self.users.find_by_email(email):
            raise ValueError("Cette adresse email est deja utilisee")

        password_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        user = self.users.create_user(nom, email, password_hash)
        self.db.commit()
        return user_to_dict(user)

    def request_recruiter_role(self, user_id: int, entreprise: str = "", referent_rh: str = ""):
        entreprise = (entreprise or "").strip()
        referent_rh = (referent_rh or "").strip()

        if not entreprise:
            raise ValueError("Nom de l'entreprise requis")
        if not referent_rh:
            raise ValueError("Referent RH requis")

        user = self.users.find_by_id(user_id)
        if not user:
            raise ValueError("Utilisateur introuvable")
        if user.role == "recruteur":
            raise ValueError("Le compte possede deja les droits recruteur")
        if user.statut_demande_recruteur == "en_attente":
            raise ValueError("Une demande recruteur est deja en attente")

        self.users.mark_recruiter_request_pending(user, entreprise, referent_rh)
        self.db.commit()
        return user_to_dict(user)

    def login(self, email: str, password: str):
        email = (email or "").strip().lower()
        if not email or not password:
            raise ValueError("Email et mot de passe requis")

        user = self.users.find_by_email(email)
        if not user or not bcrypt.checkpw(password.encode(), user.mot_de_passe_hash.encode()):
            raise PermissionError("Email ou mot de passe incorrect")

        return user_to_dict(user)
