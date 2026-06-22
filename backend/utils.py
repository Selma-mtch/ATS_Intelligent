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
