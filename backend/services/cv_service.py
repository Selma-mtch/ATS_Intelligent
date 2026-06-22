import re
from datetime import datetime
from pathlib import Path

import fitz
from werkzeug.utils import secure_filename

from config import MAX_CV_SIZE_MB, UPLOAD_FOLDER
from models import CV, Candidat, Chunk


# Quelques titres courants qu'on retrouve dans les CV.
SECTION_TITLES = {
    "skills": r"(skills|competences|compétences|technical skills|savoir-faire)",
    "experience": r"(experience|expérience|experiences|expériences|work experience|parcours professionnel)",
    "education": r"(education|formation|formations|diplome|diplôme|etudes|études)",
    "projects": r"(projects|projets|project experience)",
    "languages": r"(languages|langues)",
    "certifications": r"(certifications|certificates|certificats)",
}


class CVService:
    def __init__(self, db):
        self.db = db

    def upload_cv(self, candidat_id, uploaded_file):
        self._check_pdf(uploaded_file)

        candidat = self.db.get(Candidat, candidat_id)
        if not candidat:
            raise ValueError("Profil candidat introuvable")

        pdf_path = self._save_pdf(candidat_id, uploaded_file)
        text = self._extract_text(pdf_path)
        if not text.strip():
            pdf_path.unlink(missing_ok=True)
            raise ValueError("Le PDF ne contient pas de texte exploitable")

        chunks = split_cv_sections(text)
        if not chunks:
            pdf_path.unlink(missing_ok=True)
            raise ValueError("Impossible de decouper le CV")

        if candidat.cv:
            self.db.delete(candidat.cv)
            self.db.flush()

        cv = CV(
            candidat_id=candidat.id,
            fichier_pdf=str(pdf_path),
            texte_extrait=text,
        )
        self.db.add(cv)
        self.db.flush()

        for section_type, content in chunks:
            self.db.add(Chunk(cv_id=cv.id, type_section=section_type, contenu=content))

        self.db.commit()

        return {
            "cv_id": cv.id,
            "filename": pdf_path.name,
            "taille_texte": len(text),
            "chunks": [
                {"type_section": section_type, "contenu": content}
                for section_type, content in chunks
            ],
        }

    def _check_pdf(self, uploaded_file):
        if not uploaded_file:
            raise ValueError("Aucun fichier envoye")

        filename = secure_filename(uploaded_file.filename or "")
        if not filename.lower().endswith(".pdf"):
            raise ValueError("Le fichier doit etre un PDF")

        uploaded_file.stream.seek(0, 2)
        size = uploaded_file.stream.tell()
        uploaded_file.stream.seek(0)

        max_size = MAX_CV_SIZE_MB * 1024 * 1024
        if size > max_size:
            raise ValueError(f"Le fichier est trop lourd ({MAX_CV_SIZE_MB} Mo maximum)")
        if size == 0:
            raise ValueError("Le fichier est vide")

    def _save_pdf(self, candidat_id, uploaded_file):
        filename = secure_filename(uploaded_file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        folder = Path(UPLOAD_FOLDER) / "cvs" / f"candidat_{candidat_id}"
        folder.mkdir(parents=True, exist_ok=True)

        path = folder / f"{timestamp}_{filename}"
        uploaded_file.save(path)
        return path

    def _extract_text(self, pdf_path):
        try:
            doc = fitz.open(pdf_path)
        except Exception as error:
            raise ValueError("Impossible d'ouvrir le PDF") from error

        parts = []
        try:
            for page in doc:
                parts.append(page.get_text("text"))
        finally:
            doc.close()

        return "\n".join(parts).strip()


def split_cv_sections(text):
    matches = list(_section_title_regex().finditer(text))

    if not matches:
        return _chunk_by_paragraphs(text)

    chunks = []
    for index, match in enumerate(matches):
        section_type = _guess_section_type(match.group("title"))
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        content = text[start:end].strip(" :\n\t")

        if content:
            chunks.append((section_type, _clean_text(content)))

    if chunks:
        return chunks

    return _chunk_by_paragraphs(text)


def _section_title_regex():
    joined_titles = "|".join(SECTION_TITLES.values())
    return re.compile(rf"(?im)^\s*(?P<title>{joined_titles})\s*:?\s*$")


def _guess_section_type(title):
    title = title.lower()
    for section_type, pattern in SECTION_TITLES.items():
        if re.search(pattern, title, re.IGNORECASE):
            return section_type
    return "general"


def _chunk_by_paragraphs(text):
    paragraphs = re.split(r"\n\s*\n+", text)
    chunks = []
    for paragraph in paragraphs:
        cleaned = _clean_text(paragraph)
        if len(cleaned) >= 30:
            chunks.append(("general", cleaned))
    return chunks


def _clean_text(value):
    lines = [line.strip() for line in value.splitlines() if line.strip()]
    return "\n".join(lines)
