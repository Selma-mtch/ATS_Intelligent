from models import Candidature


class CandidatureRepository:
    def __init__(self, db):
        self.db = db

    def find_by_candidat_and_offre(self, candidat_id: int, offre_id: int):
        return (
            self.db.query(Candidature)
            .filter_by(candidat_id=candidat_id, offre_id=offre_id)
            .first()
        )

    def create(self, candidat_id: int, offre_id: int):
        candidature = Candidature(candidat_id=candidat_id, offre_id=offre_id)
        self.db.add(candidature)
        self.db.flush()
        return candidature

    def list_by_candidat(self, candidat_id: int):
        return (
            self.db.query(Candidature)
            .filter_by(candidat_id=candidat_id)
            .order_by(Candidature.date_postulation.desc())
            .all()
        )

    def list_by_offre(self, offre_id: int):
        return (
            self.db.query(Candidature)
            .filter_by(offre_id=offre_id)
            .order_by(Candidature.date_postulation.desc())
            .all()
        )

    def update_statut(self, candidature: Candidature, statut: str):
        candidature.statut = statut
