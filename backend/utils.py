def user_to_dict(user):
    return {
        "id": user.id,
        "nom": user.nom,
        "email": user.email,
        "role": user.role,
        "demande_role_recruteur": user.demande_role_recruteur,
        "statut_demande_recruteur": user.statut_demande_recruteur,
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
