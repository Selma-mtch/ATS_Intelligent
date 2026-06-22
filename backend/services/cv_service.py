import os
import uuid

from repositories.cv_repository import CVRepository

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")


def cv_to_dict(cv):
    return {
        "id": cv.id,
        "candidat_id": cv.candidat_id,
        "fichier_pdf": cv.fichier_pdf,
        "texte_extrait": cv.texte_extrait,
        "date_upload": cv.date_upload.isoformat() if cv.date_upload else None,
    }


class CVService:
    def __init__(self, db):
        self.db = db
        self.cvs = CVRepository(db)

    def upload(self, user, file_storage):
        if not user.candidat:
            raise ValueError("Profil candidat introuvable")

        if not file_storage or not file_storage.filename:
            raise ValueError("Fichier PDF requis")

        if not file_storage.filename.lower().endswith(".pdf"):
            raise ValueError("Seuls les fichiers PDF sont acceptes")

        existing = self.cvs.find_by_candidat(user.candidat.id)
        if existing:
            old_path = os.path.join(UPLOAD_DIR, existing.fichier_pdf)
            if os.path.exists(old_path):
                os.remove(old_path)
            self.cvs.delete(existing)
            self.db.flush()

        os.makedirs(UPLOAD_DIR, exist_ok=True)
        filename = f"{uuid.uuid4().hex}.pdf"
        filepath = os.path.join(UPLOAD_DIR, filename)
        file_storage.save(filepath)

        texte = self._extract_text(filepath)
        cv = self.cvs.create(user.candidat.id, filename, texte)
        self.db.commit()
        return cv_to_dict(cv)

    def get(self, user):
        if not user.candidat:
            return None
        cv = self.cvs.find_by_candidat(user.candidat.id)
        if not cv:
            return None
        return cv_to_dict(cv)

    def _extract_text(self, filepath):
        try:
            import PyPDF2
            with open(filepath, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                return "\n".join(page.extract_text() or "" for page in reader.pages).strip() or None
        except ImportError:
            return None
