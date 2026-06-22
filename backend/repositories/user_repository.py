from models import (
    Candidat,
    Recruteur,
    STATUT_DEMANDE_APPROUVEE,
    STATUT_DEMANDE_EN_ATTENTE,
    User,
)


class UserRepository:
    def __init__(self, db):
        self.db = db

    def find_by_email(self, email: str):
        return self.db.query(User).filter_by(email=email).first()

    def find_by_id(self, user_id: int):
        return self.db.get(User, user_id)

    def create_user(self, nom: str, email: str, password_hash: str):
        user = User(nom=nom, email=email, mot_de_passe_hash=password_hash, role="candidat")
        self.db.add(user)
        self.db.flush()
        self.db.add(Candidat(user_id=user.id))
        return user

    def mark_recruiter_request_pending(self, user: User, entreprise: str, referent_rh: str):
        user.demande_role_recruteur = "oui"
        user.statut_demande_recruteur = STATUT_DEMANDE_EN_ATTENTE
        user.entreprise_demande_recruteur = entreprise
        user.referent_rh_demande_recruteur = referent_rh
        return user

    def grant_recruiter_role(self, user: User, entreprise: str):
        user.role = "recruteur"
        user.demande_role_recruteur = "oui"
        user.statut_demande_recruteur = STATUT_DEMANDE_APPROUVEE
        self.db.flush()
        if not user.recruteur:
            self.db.add(Recruteur(user_id=user.id, entreprise=entreprise))
        else:
            user.recruteur.entreprise = entreprise
        return user
