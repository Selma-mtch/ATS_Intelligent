from repositories.candidature_repository import CandidatureRepository
from repositories.offre_repository import OffreRepository


def candidature_to_dict(c):
    result = {
        "id": c.id,
        "candidat_id": c.candidat_id,
        "offre_id": c.offre_id,
        "date_postulation": c.date_postulation.isoformat() if c.date_postulation else None,
        "statut": c.statut,
        "score": c.score,
    }
    if c.offre:
        result["offre_titre"] = c.offre.titre
        result["entreprise"] = c.offre.recruteur.entreprise if c.offre.recruteur else None
    if c.candidat and c.candidat.utilisateur:
        result["candidat_nom"] = c.candidat.utilisateur.nom
        result["candidat_email"] = c.candidat.utilisateur.email
    return result


class CandidatureService:
    def __init__(self, db):
        self.db = db
        self.candidatures = CandidatureRepository(db)
        self.offres = OffreRepository(db)

    def postuler(self, user, offre_id: int):
        if not user.candidat:
            raise ValueError("Profil candidat introuvable")

        offre = self.offres.find_by_id(offre_id)
        if not offre:
            raise ValueError("Offre introuvable")

        existing = self.candidatures.find_by_candidat_and_offre(user.candidat.id, offre_id)
        if existing:
            raise ValueError("Candidature deja deposee pour cette offre")

        candidature = self.candidatures.create(user.candidat.id, offre_id)
        self.db.commit()
        return candidature_to_dict(candidature)

    def list_by_candidat(self, user):
        if not user.candidat:
            return []
        return [candidature_to_dict(c) for c in self.candidatures.list_by_candidat(user.candidat.id)]

    def list_by_offre(self, user, offre_id: int):
        offre = self.offres.find_by_id(offre_id)
        if not offre:
            raise ValueError("Offre introuvable")
        if not user.recruteur or offre.recruteur_id != user.recruteur.id:
            raise PermissionError("Action non autorisee")
        return [candidature_to_dict(c) for c in self.candidatures.list_by_offre(offre_id)]

    def update_statut(self, user, candidature_id: int, statut: str):
        from models import Candidature
        candidature = self.db.get(Candidature, candidature_id)
        if not candidature:
            raise ValueError("Candidature introuvable")
        if not user.recruteur or candidature.offre.recruteur_id != user.recruteur.id:
            raise PermissionError("Action non autorisee")
        self.candidatures.update_statut(candidature, statut)
        self.db.commit()
        return candidature_to_dict(candidature)
