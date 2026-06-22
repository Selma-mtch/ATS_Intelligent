from models import Offre


class OffreRepository:
    def __init__(self, db):
        self.db = db

    def create(self, recruteur_id: int, titre: str, description: str, competences: str):
        offre = Offre(
            recruteur_id=recruteur_id,
            titre=titre,
            description=description,
            competences=competences,
        )
        self.db.add(offre)
        self.db.flush()
        return offre

    def find_by_id(self, offre_id: int):
        return self.db.get(Offre, offre_id)

    def list_all(self):
        return self.db.query(Offre).order_by(Offre.date_publication.desc()).all()

    def list_by_recruteur(self, recruteur_id: int):
        return (
            self.db.query(Offre)
            .filter_by(recruteur_id=recruteur_id)
            .order_by(Offre.date_publication.desc())
            .all()
        )

    def delete(self, offre: Offre):
        self.db.delete(offre)
