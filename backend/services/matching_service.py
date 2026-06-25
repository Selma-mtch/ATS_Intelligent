import numpy as np
from models import Offre, Candidat
from services.vector_service import VectorService

class MatchingService:
    def __init__(self, db):
        self.db = db
        self.vector_service = VectorService()

    def _cosine_similarity(self, v1, v2):
        """Calcule la similarité cosinus pure entre deux vecteurs Numpy."""
        norm1 = np.linalg.norm(v1)
        norm2 = np.linalg.norm(v2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(np.dot(v1, v2) / (norm1 * norm2))

    def get_recommended_offers(self, cv_chunks):
        """
        SENS 1 : CV -> Offres (Pour le Candidat)
        Calcule l'adéquation d'un CV face à toutes les offres d'emploi.
        """
        # On récupère toutes les offres qui possèdent une référence d'embedding FAISS
        offers = self.db.query(Offre).filter(Offre.embedding_ref != None).all()
        if not cv_chunks or not offers:
            return []

        recommendations = []
        for offer in offers:
            # On extrait l'ID numérique de la chaîne "faiss_ID" (ex: "faiss_4" -> 4)
            try:
                offer_faiss_id = int(offer.embedding_ref.split("_")[1])
                offer_vector = self.vector_service.get_vector_by_id(offer_faiss_id)
            except (IndexError, ValueError, TypeError):
                continue

            if offer_vector is None:
                continue

            chunk_scores = []
            for chunk in cv_chunks:
                if chunk.embedding_ref:
                    try:
                        chunk_faiss_id = int(chunk.embedding_ref.split("_")[1])
                        chunk_vector = self.vector_service.get_vector_by_id(chunk_faiss_id)
                        
                        if chunk_vector is not None:
                            # Calcul de la similarité entre le morceau de CV et l'offre d'emploi
                            score = self._cosine_similarity(chunk_vector, offer_vector)
                            chunk_scores.append(score)
                    except (IndexError, ValueError, TypeError):
                        continue
            
            # Score final du candidat = moyenne des similarités de ses chunks
            final_score = np.mean(chunk_scores) if chunk_scores else 0.0
            
            recommendations.append({
                "id": offer.id,
                "titre": offer.titre,
                "domaine": getattr(offer, "domaine", "Général"),
                "type_contrat": getattr(offer, "type_contrat", "Non spécifié"),
                "score": round(final_score * 100, 2)  # Score converti en pourcentage
            })

        # Tri des offres de la plus pertinente à la moins pertinente
        return sorted(recommendations, key=lambda x: x["score"], reverse=True)

    def get_candidates_for_offer(self, offer_embedding_ref):
        """
        SENS 2 : Offre -> CVs (Pour le Recruteur)
        Classe tous les candidats de la BDD par ordre de pertinence pour une offre donnée.
        """
        try:
            offer_faiss_id = int(offer_embedding_ref.split("_")[1])
            offer_vector = self.vector_service.get_vector_by_id(offer_faiss_id)
        except (IndexError, ValueError, TypeError):
            return []

        if offer_vector is None:
            return []

        # On récupère tous les candidats qui possèdent un CV attaché
        candidates = self.db.query(Candidat).join(Candidat.cv).all()
        ranked_candidates = []

        for candidate in candidates:
            if not candidate.cv or not candidate.cv.chunks:
                continue
                
            chunk_scores = []
            for chunk in candidate.cv.chunks:
                if chunk.embedding_ref:
                    try:
                        chunk_faiss_id = int(chunk.embedding_ref.split("_")[1])
                        chunk_vector = self.vector_service.get_vector_by_id(chunk_faiss_id)
                        
                        if chunk_vector is not None:
                            score = self._cosine_similarity(offer_vector, chunk_vector)
                            chunk_scores.append(score)
                    except (IndexError, ValueError, TypeError):
                        continue
                    
            final_score = np.mean(chunk_scores) if chunk_scores else 0.0
            
            ranked_candidates.append({
                "user_id": candidate.id,
                "nom": candidate.nom,
                "email": candidate.email,
                "score": round(final_score * 100, 2)
            })
            
        # Tri des candidats par score décroissant
        return sorted(ranked_candidates, key=lambda x: x["score"], reverse=True)