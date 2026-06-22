from repositories.offre_repository import OffreRepository
from utils import offre_to_dict


class OffreService:
    def __init__(self, db):
        self.db = db
        self.offres = OffreRepository(db)

    def create_offre(self, recruteur_id: int, data: dict):
        titre = (data.get("titre", "") or "").strip()
        type_contrat = (data.get("type_contrat", "") or "").strip()
        duree_contrat = (data.get("duree_contrat", "") or "").strip()
        domaine = (data.get("domaine", "") or "").strip()
        competences = (data.get("competences", "") or "").strip()
        description_entreprise = (data.get("description_entreprise", "") or "").strip()
        description = (data.get("description", "") or "").strip()

        manquants = []
        if not titre:
            manquants.append("nom du poste")
        if not type_contrat:
            manquants.append("type de contrat")
        if not domaine:
            manquants.append("domaine")
        if not competences:
            manquants.append("competences requises")
        if not description:
            manquants.append("description des missions")
        if manquants:
            raise ValueError("Champs requis manquants : " + ", ".join(manquants))

        offre = self.offres.create(
            recruteur_id,
            titre=titre,
            type_contrat=type_contrat,
            duree_contrat=duree_contrat,
            domaine=domaine,
            competences=competences,
            description_entreprise=description_entreprise,
            description=description,
        )
        self.db.commit()
        return offre_to_dict(offre)

    def list_mes_offres(self, recruteur_id: int):
        return [offre_to_dict(offre) for offre in self.offres.list_by_recruteur(recruteur_id)]
