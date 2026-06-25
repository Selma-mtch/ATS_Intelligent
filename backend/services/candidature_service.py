from models import Offre
from repositories.candidature_repository import CandidatureRepository
from utils import candidature_to_dict, cv_to_dict


STATUTS_AUTORISES = {"deposee", "acceptee", "refusee"}


class CandidatureService:
    def __init__(self, db):
        self.db = db
        self.candidatures = CandidatureRepository(db)

    def postuler(self, candidat_id: int, offre_id):
        if not offre_id:
            raise ValueError("Offre requise")

        offre = self.db.get(Offre, offre_id)
        if not offre:
            raise ValueError("Offre introuvable")
        if self.candidatures.find(candidat_id, offre_id):
            raise ValueError("Vous avez deja postule a cette offre")

        candidature = self.candidatures.create(candidat_id, offre_id)
        self.db.commit()
        return candidature_to_dict(candidature)

    def list_mes_candidatures(self, candidat_id: int):
        return [
            candidature_to_dict(candidature)
            for candidature in self.candidatures.list_by_candidat(candidat_id)
        ]

    def list_candidats_offre(self, offre_id: int):
        return [
            candidature_to_dict(candidature)
            for candidature in self.candidatures.list_by_offre(offre_id)
        ]

    def changer_statut(self, recruteur_id: int, candidature_id: int, statut):
        statut = (statut or "").strip()
        if statut not in STATUTS_AUTORISES:
            raise ValueError("Statut invalide")

        candidature = self.candidatures.find_by_id(candidature_id)
        if not candidature:
            raise ValueError("Candidature introuvable")
        if not candidature.offre or candidature.offre.recruteur_id != recruteur_id:
            raise PermissionError("Cette candidature ne concerne pas vos offres")

        candidature.statut = statut
        self.db.commit()
        return candidature_to_dict(candidature)

    def get_cv_candidature(self, recruteur_id: int, candidature_id: int):
        candidature = self.candidatures.find_by_id(candidature_id)
        if not candidature:
            raise ValueError("Candidature introuvable")
        if not candidature.offre or candidature.offre.recruteur_id != recruteur_id:
            raise PermissionError("Cette candidature ne concerne pas vos offres")

        candidat = candidature.candidat
        cvs = candidat.cvs if candidat else []
        if not cvs:
            return None
        cv = next((c for c in cvs if c.est_selectionne == "oui"), cvs[0])
        return cv_to_dict(cv)
