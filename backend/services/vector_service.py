import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

FAISS_INDEX_PATH = "ats_index.faiss"
VECTOR_DIMENSION = 384

class VectorService:
    def __init__(self):
        self.model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
        
        self.index = self._load_or_create_index()

    def _load_or_create_index(self):
        """Charge l'index existant depuis le disque ou en crée un nouveau."""
        if os.path.exists(FAISS_INDEX_PATH):
            return faiss.read_index(FAISS_INDEX_PATH)
        else:
            # IndexIDMap permet d'associer un ID entier personnalisé à chaque vecteur
            quantizer = faiss.IndexFlatIP(VECTOR_DIMENSION) # Similarité Cosinus / Produit scalaire
            return faiss.IndexIDMap(quantizer)

    def _save_index(self):
        """Sauvegarde l'état actuel de l'index sur le disque."""
        faiss.write_index(self.index, FAISS_INDEX_PATH)

    def add_text_to_index(self, text: str, custom_id: int) -> str:
        """
        Prend un texte, le transforme en vecteur, l'ajoute à FAISS
        et retourne la chaîne de référence à mettre en BDD.
        """
        if not text or not text.strip():
            return None

        # Générer le vecteur (embedding) et le forcer au format float32 (requis par FAISS)
        embedding = self.model.encode(text)
        vector_np = np.array([embedding]).astype("float32")

        # Normaliser le vecteur pour que le produit scalaire (Inner Product) équivale à la Similarité Cosinus
        faiss.normalize_L2(vector_np)

        # Ajouter à l'index FAISS avec l'ID personnalisé
        self.index.add_with_ids(vector_np, np.array([custom_id], dtype=np.int64))
        self._save_index()

        return f"faiss_{custom_id}"

    def get_vector_by_id(self, custom_id: int):
        """Récupère un vecteur spécifique depuis l'index FAISS via son ID."""
        try:
            # Reconstruction du vecteur depuis l'index
            return self.index.reconstruct(custom_id)
        except Exception:
            return None