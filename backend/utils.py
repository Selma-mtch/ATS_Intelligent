def user_to_dict(user):
    return {
        "id": user.id,
        "nom": user.nom,
        "email": user.email,
        "role": user.role,
        "demande_role_recruteur": user.demande_role_recruteur,
        "statut_demande_recruteur": user.statut_demande_recruteur,
        "entreprise_demande_recruteur": user.entreprise_demande_recruteur,
        "referent_rh_demande_recruteur": user.referent_rh_demande_recruteur,
    }


def offre_to_dict(offre):
    return {
        "id": offre.id,
        "titre": offre.titre,
        "type_contrat": offre.type_contrat,
        "duree_contrat": offre.duree_contrat,
        "domaine": offre.domaine,
        "competences": offre.competences,
        "description_entreprise": offre.description_entreprise,
        "description": offre.description,
        "date_publication": offre.date_publication.isoformat() if offre.date_publication else None,
    }


def candidature_to_dict(candidature):
    offre = candidature.offre
    candidat = candidature.candidat
    utilisateur = candidat.utilisateur if candidat else None
    return {
        "id": candidature.id,
        "statut": candidature.statut,
        "date_postulation": candidature.date_postulation.isoformat() if candidature.date_postulation else None,
        "offre_id": candidature.offre_id,
        "offre_titre": offre.titre if offre else None,
        "candidat_id": candidature.candidat_id,
        "candidat_nom": utilisateur.nom if utilisateur else None,
        "candidat_email": utilisateur.email if utilisateur else None,
    }


def cv_to_dict(cv):
    return {
        "id": cv.id,
        "fichier_pdf": cv.fichier_pdf,
        "texte_extrait": cv.texte_extrait,
        "chunks": [
            {"id": chunk.id, "type_section": chunk.type_section, "contenu": chunk.contenu}
            for chunk in cv.chunks
        ],
    }
