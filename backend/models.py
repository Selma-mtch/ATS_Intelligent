from sqlalchemy import JSON
from datetime import datetime, timezone
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


ROLE_CANDIDAT = "candidat"
ROLE_RECRUTEUR = "recruteur"
ROLE_ADMINISTRATEUR = "administrateur"

STATUT_DEMANDE_AUCUNE = "aucune"
STATUT_DEMANDE_EN_ATTENTE = "en_attente"
STATUT_DEMANDE_APPROUVEE = "approuvee"
STATUT_DEMANDE_REFUSEE = "refusee"


def now_utc():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    nom = Column(String(120), nullable=False)
    email = Column(String(160), unique=True, nullable=False)
    mot_de_passe_hash = Column(String(255), nullable=False)
    role = Column(String(30), nullable=False)
    demande_role_recruteur = Column(String(10), nullable=False, default="non")
    statut_demande_recruteur = Column(String(30), nullable=False, default=STATUT_DEMANDE_AUCUNE)
    entreprise_demande_recruteur = Column(String(160), nullable=True)
    referent_rh_demande_recruteur = Column(String(160), nullable=True)
    created_at = Column(DateTime, default=now_utc)

    candidat = relationship("Candidat", back_populates="utilisateur", uselist=False, cascade="all, delete-orphan")
    recruteur = relationship("Recruteur", back_populates="utilisateur", uselist=False, cascade="all, delete-orphan")
    administrateur = relationship("Administrateur", back_populates="utilisateur", uselist=False, cascade="all, delete-orphan")


class Candidat(Base):
    __tablename__ = "candidats"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    utilisateur = relationship("User", back_populates="candidat")
    cv = relationship("CV", back_populates="candidat", uselist=False, cascade="all, delete-orphan")
    candidatures = relationship("Candidature", back_populates="candidat", cascade="all, delete-orphan")


class Recruteur(Base):
    __tablename__ = "recruteurs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    entreprise = Column(String(160), nullable=False)

    utilisateur = relationship("User", back_populates="recruteur")
    offres = relationship("Offre", back_populates="recruteur", cascade="all, delete-orphan")


class Administrateur(Base):
    __tablename__ = "administrateurs"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)

    utilisateur = relationship("User", back_populates="administrateur")


class CV(Base):
    __tablename__ = "cvs"

    id = Column(Integer, primary_key=True)
    candidat_id = Column(Integer, ForeignKey("candidats.id"), nullable=False)
    fichier_pdf = Column(String(255), nullable=False)
    texte_extrait = Column(Text, nullable=True)
    date_upload = Column(DateTime, default=now_utc)

    candidat = relationship("Candidat", back_populates="cv")
    chunks = relationship("Chunk", back_populates="cv", cascade="all, delete-orphan")


class Chunk(Base):
    __tablename__ = "cv_chunks"

    id = Column(Integer, primary_key=True)
    cv_id = Column(Integer, ForeignKey("cvs.id"), nullable=False)
    type_section = Column(String(80), nullable=False)
    contenu = Column(Text, nullable=False)
    embedding_ref = Column(String(255), nullable=True)

    cv = relationship("CV", back_populates="chunks")


class Offre(Base):
    __tablename__ = "offres"

    id = Column(Integer, primary_key=True)
    recruteur_id = Column(Integer, ForeignKey("recruteurs.id"), nullable=False)
    titre = Column(String(180), nullable=False)
    type_contrat = Column(String(60), nullable=True)
    duree_contrat = Column(String(80), nullable=True)
    domaine = Column(String(120), nullable=True)
    competences = Column(Text, nullable=True)
    description_entreprise = Column(Text, nullable=True)
    description = Column(Text, nullable=False)
    date_publication = Column(DateTime, default=now_utc)

    recruteur = relationship("Recruteur", back_populates="offres")
    candidatures = relationship("Candidature", back_populates="offre", cascade="all, delete-orphan")


class Candidature(Base):
    __tablename__ = "candidatures"
    __table_args__ = (
        UniqueConstraint("candidat_id", "offre_id", name="uq_candidature_candidat_offre"),
    )

    id = Column(Integer, primary_key=True)
    candidat_id = Column(Integer, ForeignKey("candidats.id"), nullable=False)
    offre_id = Column(Integer, ForeignKey("offres.id"), nullable=False)
    date_postulation = Column(DateTime, default=now_utc)
    statut = Column(String(80), nullable=False, default="deposee")
    score = Column(Float, nullable=True)

    candidat = relationship("Candidat", back_populates="candidatures")
    offre = relationship("Offre", back_populates="candidatures")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    role = Column(String(30), nullable=False)
    contenu = Column(Text, nullable=False)
    created_at = Column(DateTime, default=now_utc)


class MoteurIA(Base):
    __tablename__ = "moteur_ia"

    id = Column(Integer, primary_key=True)
    modele_embedding = Column(String(180), nullable=False, default="sentence-transformers/all-MiniLM-L6-v2")
    index_faiss = Column(String(255), nullable=True)


class LLMCopilote(Base):
    __tablename__ = "llm_copilote"

    id = Column(Integer, primary_key=True)
    modele = Column(String(180), nullable=False)
