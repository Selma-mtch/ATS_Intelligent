from repositories.user_repository import UserRepository
from utils import user_to_dict


class AdminService:
    def __init__(self, db):
        self.db = db
        self.users = UserRepository(db)

    def grant_recruiter_role(self, user_id: int, entreprise: str):
        entreprise = (entreprise or "").strip()
        if not entreprise:
            raise ValueError("Entreprise requise")

        user = self.users.find_by_id(user_id)
        if not user:
            raise ValueError("Utilisateur introuvable")
        if user.statut_demande_recruteur != "en_attente":
            raise ValueError("Aucune demande recruteur en attente pour cet utilisateur")

        self.users.grant_recruiter_role(user, entreprise)
        self.db.commit()
        return user_to_dict(user)

    def reject_recruiter_role(self, user_id: int):
        user = self.users.find_by_id(user_id)
        if not user:
            raise ValueError("Utilisateur introuvable")
        if user.statut_demande_recruteur != "en_attente":
            raise ValueError("Aucune demande recruteur en attente pour cet utilisateur")

        self.users.reject_recruiter_request(user)
        self.db.commit()
        return user_to_dict(user)
