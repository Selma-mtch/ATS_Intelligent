from repositories.offre_repository import OffreRepository


def offre_to_dict(offre):
    return {
        "id": offre.id,
        "recruteur_id": offre.recruteur_id,
        "titre": offre.titre,
        "description": offre.description,
        "competences": offre.competences,
        "date_publication": offre.date_publication.isoformat() if offre.date_publication else None,
        "recruteur_nom": offre.recruteur.utilisateur.nom if offre.recruteur else None,
        "entreprise": offre.recruteur.entreprise if offre.recruteur else None,
    }


class OffreService:
    def __init__(self, db):
        self.db = db
        self.offres = OffreRepository(db)

    def create(self, user, titre: str, description: str, competences: str):
        titre = (titre or "").strip()
        description = (description or "").strip()
        competences = (competences or "").strip()

        if not titre:
            raise ValueError("Titre requis")
        if not description:
            raise ValueError("Description requise")

        if not user.recruteur:
            raise ValueError("Profil recruteur introuvable")

        offre = self.offres.create(user.recruteur.id, titre, description, competences)
        self.db.commit()
        return offre_to_dict(offre)

    def list_all(self):
        return [offre_to_dict(o) for o in self.offres.list_all()]

    def list_by_recruteur(self, user):
        if not user.recruteur:
            raise ValueError("Profil recruteur introuvable")
        return [offre_to_dict(o) for o in self.offres.list_by_recruteur(user.recruteur.id)]

    def get(self, offre_id: int):
        offre = self.offres.find_by_id(offre_id)
        if not offre:
            raise ValueError("Offre introuvable")
        return offre_to_dict(offre)

    def delete(self, user, offre_id: int):
        offre = self.offres.find_by_id(offre_id)
        if not offre:
            raise ValueError("Offre introuvable")
        if not user.recruteur or offre.recruteur_id != user.recruteur.id:
            raise PermissionError("Action non autorisee")
        self.offres.delete(offre)
        self.db.commit()
