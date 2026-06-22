from models import CV


class CVRepository:
    def __init__(self, db):
        self.db = db

    def find_by_candidat(self, candidat_id: int):
        return self.db.query(CV).filter_by(candidat_id=candidat_id).first()

    def create(self, candidat_id: int, fichier_pdf: str, texte_extrait: str = None):
        cv = CV(
            candidat_id=candidat_id,
            fichier_pdf=fichier_pdf,
            texte_extrait=texte_extrait,
        )
        self.db.add(cv)
        self.db.flush()
        return cv

    def update_text(self, cv: CV, texte_extrait: str):
        cv.texte_extrait = texte_extrait

    def delete(self, cv: CV):
        self.db.delete(cv)
