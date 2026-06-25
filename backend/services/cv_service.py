import re
import unicodedata
from datetime import datetime
from pathlib import Path

import fitz
from werkzeug.utils import secure_filename

from config import MAX_CV_SIZE_MB, UPLOAD_FOLDER
from models import CV, Candidat, Chunk


# Titres normalises utilises pour decouper les CV.
# Cette liste evite les problemes d'accents et de majuscules dans les PDF.
TITRES_SECTIONS = {
    "skills": (
        "skills",
        "competences",
        "competences techniques",
        "competences professionnelles",
        "technical skills",
        "hard skills",
        "savoir faire",
        "technologies",
        "outils",
    ),
    "experience": (
        "experience",
        "experiences",
        "experience professionnelle",
        "experiences professionnelles",
        "work experience",
        "parcours professionnel",
    ),
    "education": (
        "education",
        "formation",
        "formations",
        "diplome",
        "etudes",
        "parcours academique",
    ),
    "projets": (
        "projects",
        "projets",
        "projets universitaires",
        "projets academiques",
        "projets professionnels",
        "project experience",
        "realisations",
    ),
    "langues": (
        "langues",
        "langue",
        "languages",
        "language",
        "soft skills & langues",
        "soft skills et langues",
    ),
    "certifications": (
        "certifications",
        "certificats",
        "certificates",
        "certifications & langues",
        "certifications et langues",
    ),
    "interets": (
        "centres d'interet",
        "centres d interet",
        "interets",
        "hobbies",
        "loisirs",
    ),
    "resume": (
        "summary",
        "resume",
        "resume professionnel",
        "profil",
        "about me",
        "a propos de moi",
        "presentation",
    ),
}


class CVService:
    def __init__(self, db):
        self.db = db

    def upload_cv(self, candidat_id, uploaded_file):
        self._verifier_pdf(uploaded_file)

        candidat = self.db.get(Candidat, candidat_id)
        if not candidat:
            raise ValueError("Profil candidat introuvable")

        chemin_pdf = self._sauvegarder_pdf(candidat_id, uploaded_file)
        texte_extrait = self._extraire_texte_pdf(chemin_pdf)
        if not texte_extrait.strip():
            chemin_pdf.unlink(missing_ok=True)
            raise ValueError("Le PDF ne contient pas de texte exploitable")

        blocs_cv = split_cv_sections(texte_extrait)
        if not blocs_cv:
            chemin_pdf.unlink(missing_ok=True)
            raise ValueError("Impossible de decouper le CV")

        a_deja_un_cv_selectionne = any(cv.est_selectionne == "oui" for cv in candidat.cvs)
        cv = CV(
            candidat_id=candidat.id,
            nom_fichier=uploaded_file.filename,
            fichier_pdf=str(chemin_pdf),
            texte_extrait=texte_extrait,
            est_selectionne="non" if a_deja_un_cv_selectionne else "oui",
        )
        self.db.add(cv)
        self.db.flush()

        for type_section, contenu_section in blocs_cv:
            self.db.add(Chunk(cv_id=cv.id, type_section=type_section, contenu=contenu_section))

        self.db.commit()

        return {
            "cv_id": cv.id,
            "filename": cv.nom_fichier or chemin_pdf.name,
            "est_selectionne": cv.est_selectionne,
            "taille_texte": len(texte_extrait),
            "chunks": [
                {"type_section": type_section, "contenu": contenu_section}
                for type_section, contenu_section in blocs_cv
            ],
        }

    def list_cvs(self, candidat_id):
        cvs = (
            self.db.query(CV)
            .filter_by(candidat_id=candidat_id)
            .order_by(CV.date_upload.desc())
            .all()
        )
        return [self._cv_to_dict(cv) for cv in cvs]

    def select_cv(self, candidat_id, cv_id):
        cv = self._recuperer_cv_candidat(candidat_id, cv_id)
        for candidat_cv in cv.candidat.cvs:
            candidat_cv.est_selectionne = "oui" if candidat_cv.id == cv.id else "non"
        self.db.commit()
        return self._cv_to_dict(cv)

    def delete_cv(self, candidat_id, cv_id):
        cv = self._recuperer_cv_candidat(candidat_id, cv_id)
        etait_selectionne = cv.est_selectionne == "oui"
        chemin_pdf = Path(cv.fichier_pdf)

        self.db.delete(cv)
        self.db.flush()

        if etait_selectionne:
            prochain_cv = (
                self.db.query(CV)
                .filter_by(candidat_id=candidat_id)
                .order_by(CV.date_upload.desc())
                .first()
            )
            if prochain_cv:
                prochain_cv.est_selectionne = "oui"

        self.db.commit()
        chemin_pdf.unlink(missing_ok=True)

    def _recuperer_cv_candidat(self, candidat_id, cv_id):
        cv = self.db.get(CV, cv_id)
        if not cv or cv.candidat_id != candidat_id:
            raise ValueError("CV introuvable")
        return cv

    def _cv_to_dict(self, cv):
        nom_fichier = cv.nom_fichier or Path(cv.fichier_pdf).name
        return {
            "id": cv.id,
            "filename": nom_fichier,
            "fichier_pdf": cv.fichier_pdf,
            "texte_extrait": cv.texte_extrait,
            "date_upload": cv.date_upload.isoformat() if cv.date_upload else None,
            "est_selectionne": cv.est_selectionne,
            "chunks": [
                {
                    "id": chunk.id,
                    "type_section": chunk.type_section,
                    "contenu": chunk.contenu,
                }
                for chunk in cv.chunks
            ],
        }

    def _verifier_pdf(self, uploaded_file):
        if not uploaded_file:
            raise ValueError("Aucun fichier envoye")

        nom_fichier = secure_filename(uploaded_file.filename or "")
        if not nom_fichier.lower().endswith(".pdf"):
            raise ValueError("Le fichier doit etre un PDF")

        uploaded_file.stream.seek(0, 2)
        taille_fichier = uploaded_file.stream.tell()
        uploaded_file.stream.seek(0)

        taille_max = MAX_CV_SIZE_MB * 1024 * 1024
        if taille_fichier > taille_max:
            raise ValueError(f"Le fichier est trop lourd ({MAX_CV_SIZE_MB} Mo maximum)")
        if taille_fichier == 0:
            raise ValueError("Le fichier est vide")

    def _sauvegarder_pdf(self, candidat_id, uploaded_file):
        nom_fichier = secure_filename(uploaded_file.filename)
        horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
        dossier = Path(UPLOAD_FOLDER) / "cvs" / f"candidat_{candidat_id}"
        dossier.mkdir(parents=True, exist_ok=True)

        chemin_pdf = dossier / f"{horodatage}_{nom_fichier}"
        uploaded_file.save(chemin_pdf)
        return chemin_pdf

    def _extraire_texte_pdf(self, chemin_pdf):
        try:
            document_pdf = fitz.open(chemin_pdf)
        except Exception as error:
            raise ValueError("Impossible d'ouvrir le PDF") from error

        textes_pages = []
        try:
            for page in document_pdf:
                textes_pages.append(page.get_text("text"))
        finally:
            document_pdf.close()

        return "\n".join(textes_pages).strip()


def split_cv_sections(texte):
    titres_detectes = _trouver_titres_sections(texte)

    if not titres_detectes:
        return _creer_bloc_general(texte)

    blocs_cv = []
    for index, titre_detecte in enumerate(titres_detectes):
        type_section = titre_detecte["type_section"]
        debut_section = titre_detecte["fin"]
        fin_section = (
            titres_detectes[index + 1]["debut"]
            if index + 1 < len(titres_detectes)
            else len(texte)
        )
        contenu_section = texte[debut_section:fin_section].strip(" :\n\t")

        if contenu_section:
            blocs_cv.append((type_section, _nettoyer_texte(contenu_section)))

    if blocs_cv:
        return blocs_cv

    return _creer_bloc_general(texte)


def _trouver_titres_sections(texte):
    titres_detectes = []
    position_ligne = 0

    for ligne in texte.splitlines(keepends=True):
        debut_ligne = position_ligne
        fin_ligne = position_ligne + len(ligne)
        position_ligne = fin_ligne

        type_section = _deviner_type_section(ligne)
        if type_section:
            titres_detectes.append({
                "type_section": type_section,
                "debut": debut_ligne,
                "fin": fin_ligne,
            })

    return titres_detectes


def _deviner_type_section(titre_section):
    titre_normalise = _normaliser_titre_section(titre_section)
    if not titre_normalise:
        return None

    for type_section, titres_connus in TITRES_SECTIONS.items():
        if titre_normalise in titres_connus:
            return type_section
    return None


def _normaliser_titre_section(valeur):
    valeur = unicodedata.normalize("NFKD", valeur)
    valeur = "".join(caractere for caractere in valeur if not unicodedata.combining(caractere))
    valeur = valeur.lower()
    valeur = valeur.replace("&", " & ")
    valeur = re.sub(r"[^a-z0-9&]+", " ", valeur)
    return re.sub(r"\s+", " ", valeur).strip()


def _creer_bloc_general(texte):
    texte_nettoye = _nettoyer_texte(texte)
    if len(texte_nettoye) < 30:
        return []
    return [("general", texte_nettoye)]


def _nettoyer_texte(valeur):
    lignes = [ligne.strip() for ligne in valeur.splitlines() if ligne.strip()]
    return "\n".join(lignes)
