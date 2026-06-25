from repositories.candidature_repository import CandidatureRepository
from utils import cv_to_dict


def _cv_summary(candidat):
    """Retourne les infos du CV selectionne du candidat si disponible."""
    cvs = candidat.cvs if candidat else []
    if not cvs:
        return None
    cv = next((c for c in cvs if c.est_selectionne == "oui"), cvs[0])
    return {
        "id": cv.id,
        "fichier_pdf": cv.fichier_pdf,
        "date_upload": cv.date_upload.isoformat() if cv.date_upload else None,
        "a_texte_extrait": bool(cv.texte_extrait),
    }


def candidature_to_dict(c, include_cv=False):
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
    if include_cv:
        result["cv"] = _cv_summary(c.candidat)
    return result


class CandidatureService:
    STATUTS_VALIDES = ["deposee", "vue", "entretien", "acceptee", "refusee"]

    def __init__(self, db):
        self.db = db
        self.repo = CandidatureRepository(db)

    def postuler(self, user, offre_id: int):
        if not user.candidat:
            raise ValueError("Profil candidat introuvable")

        offre = self.repo.find_offre(offre_id)
        if not offre:
            raise ValueError("Offre introuvable")

        existing = self.repo.find_by_candidat_and_offre(user.candidat.id, offre_id)
        if existing:
            raise ValueError("Vous avez deja postule a cette offre")

        candidature = self.repo.create(user.candidat.id, offre_id)
        self.db.commit()
        return candidature_to_dict(candidature)

    def list_by_candidat(self, user):
        if not user.candidat:
            return []
        return [
            candidature_to_dict(c)
            for c in self.repo.list_by_candidat(user.candidat.id)
        ]

    def list_by_offre(self, user, offre_id: int):
        offre = self.repo.find_offre(offre_id)
        if not offre:
            raise ValueError("Offre introuvable")
        if not user.recruteur or offre.recruteur_id != user.recruteur.id:
            raise PermissionError("Action non autorisee")
        return [
            candidature_to_dict(c, include_cv=True)
            for c in self.repo.list_by_offre(offre_id)
        ]

    def update_statut(self, user, candidature_id: int, nouveau_statut: str):
        nouveau_statut = (nouveau_statut or "").strip().lower()
        if nouveau_statut not in self.STATUTS_VALIDES:
            raise ValueError(
                f"Statut invalide. Valeurs acceptees : {', '.join(self.STATUTS_VALIDES)}"
            )

        candidature = self.repo.find_by_id(candidature_id)
        if not candidature:
            raise ValueError("Candidature introuvable")

        offre = self.repo.find_offre(candidature.offre_id)
        if not user.recruteur or offre.recruteur_id != user.recruteur.id:
            raise PermissionError("Action non autorisee")

        self.repo.update_statut(candidature, nouveau_statut)
        self.db.commit()
        return candidature_to_dict(candidature, include_cv=True)

    def stats_by_offre(self, user, offre_id: int):
        offre = self.repo.find_offre(offre_id)
        if not offre:
            raise ValueError("Offre introuvable")
        if not user.recruteur or offre.recruteur_id != user.recruteur.id:
            raise PermissionError("Action non autorisee")

        candidatures = self.repo.list_by_offre(offre_id)
        counts = {s: 0 for s in self.STATUTS_VALIDES}
        for c in candidatures:
            if c.statut in counts:
                counts[c.statut] += 1
        return {"total": len(candidatures), "par_statut": counts}

    def get_cv_for_recruiter(self, user, candidature_id: int):
        candidature = self.repo.find_by_id(candidature_id)
        if not candidature:
            raise ValueError("Candidature introuvable")

        offre = self.repo.find_offre(candidature.offre_id)
        if not user.recruteur or offre.recruteur_id != user.recruteur.id:
            raise PermissionError("Action non autorisee")

        candidat = candidature.candidat
        cvs = candidat.cvs if candidat else []
        if not cvs:
            return None
        cv = next((c for c in cvs if c.est_selectionne == "oui"), cvs[0])
        return cv_to_dict(cv)
