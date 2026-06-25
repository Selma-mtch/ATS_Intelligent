import os

import requests
import streamlit as st


API_URL = os.getenv("ATS_API_URL", "http://localhost:5001").rstrip("/")


st.set_page_config(
    page_title="ATS Intelligent",
    page_icon="ATS",
    layout="wide",
    initial_sidebar_state="expanded",
)


def api_session():
    if "api_session" not in st.session_state:
        st.session_state.api_session = requests.Session()
    return st.session_state.api_session


def request_api(method, path, **kwargs):
    response = api_session().request(method, f"{API_URL}{path}", timeout=10, **kwargs)
    try:
        payload = response.json()
    except ValueError:
        if response.status_code == 404:
            payload = {"error": "Route API introuvable. Redemarre le backend Flask et verifie l'URL de l'API."}
        else:
            payload = {"error": response.text or "Reponse API illisible"}
    return response.status_code, payload


def set_user(user):
    st.session_state.user = user


def get_user():
    return st.session_state.get("user")


def logout():
    request_api("POST", "/auth/logout")
    st.session_state.pop("user", None)
    st.rerun()


def show_api_status():
    try:
        status, payload = request_api("GET", "/")
        if status == 200:
            st.sidebar.success(payload.get("message", "API en ligne"))
        else:
            st.sidebar.warning("API indisponible")
    except requests.RequestException:
        st.sidebar.error("Backend Flask non joignable")


def auth_view():
    # On crée un conteneur global pour toute la vue d'authentification
    auth_container = st.empty()
    
    with auth_container.container():
        st.title("ATS Intelligent")
        st.caption("Plateforme ATS intelligente avec IA")

        mode = st.radio(
            "Mode d'acces",
            ["Connexion", "Inscription"],
            horizontal=True,
            label_visibility="collapsed",
        )

        if mode == "Connexion":
            with st.form("login_form", clear_on_submit=False):
                email = st.text_input("Email")
                password = st.text_input("Mot de passe", type="password")
                submitted = st.form_submit_button("Se connecter", use_container_width=True)

            if submitted:
                status, payload = request_api(
                    "POST",
                    "/auth/login",
                    json={"email": email, "mot_de_passe": password},
                )
                if status == 200:
                    set_user(payload["user"])
                    # Astuce : On vide le conteneur visuel IMMÉDIATEMENT
                    auth_container.empty()
                    st.rerun()
                else:
                    st.error(payload.get("error", "Connexion impossible"))

        if mode == "Inscription":
            st.info("Tous les comptes sont crées comme candidats. Le rôle recruteur se demande ensuite depuis l'espace utilisateur.")
            with st.form("register_form", clear_on_submit=False):
                nom = st.text_input("Nom", key="register_nom")
                email = st.text_input("Email", key="register_email")
                password = st.text_input("Mot de passe", type="password", key="register_password")
                submitted = st.form_submit_button("Créer mon compte", use_container_width=True)

            if submitted:
                status, payload = request_api(
                    "POST",
                    "/auth/register",
                    json={"nom": nom, "email": email, "mot_de_passe": password},
                )
                if status == 201:
                    set_user(payload["user"])
                    # On fait de même pour l'inscription
                    auth_container.empty()
                    st.rerun()
                else:
                    st.error(payload.get("error", "Inscription impossible"))


def dashboard_header(user):
    left, right = st.columns([0.78, 0.22])
    with left:
        st.title("ATS Intelligent")
        st.caption(f"{user['nom']} - {user['role']}")
    with right:
        st.button("Se déconnecter", on_click=logout, use_container_width=True)


def cv_expander_label(filename, section_type):
    if section_type == "general":
        return f"{filename} (general)"
    return f"{filename} - {section_type}"


def candidate_dashboard(user):
    dashboard_header(user)

    cv_tab, offers_tab, applications_tab, recruiter_request_tab, chatbot_tab = st.tabs(
        ["CV", "Offres", "Candidatures", "Demande RH", "Copilote"]
    )

    with cv_tab:
        st.subheader("Depot de CV PDF")
        uploaded_cv = st.file_uploader("CV au format PDF", type=["pdf"])

        if uploaded_cv and st.button("Analyser mon CV", use_container_width=True):
            files = {
                "cv": (
                    uploaded_cv.name,
                    uploaded_cv.getvalue(),
                    "application/pdf",
                )
            }
            status, payload = request_api("POST", "/cv/upload", files=files)
            if status == 201:
                st.success("CV analyse et sauvegarde.")
                st.write(f"Texte extrait : {payload['taille_texte']} caracteres")
                st.write("Extraction trouvee :")
                for chunk in payload["chunks"]:
                    label = cv_expander_label(payload["filename"], chunk["type_section"])
                    with st.expander(label):
                        st.write(chunk["contenu"])
            else:
                st.error(payload.get("error", "Upload impossible"))

        status, payload = request_api("GET", "/cv/me")
        if status == 200:
            cvs = payload.get("cvs", [])
            selected_cv = payload.get("cv_selectionne")
            if not cvs:
                st.info("Aucun CV enregistre pour le moment.")
            else:
                st.divider()
                st.subheader("CV enregistres")
                if selected_cv:
                    st.success(f"CV utilise pour les candidatures : {selected_cv['filename']}")

                for cv in cvs:
                    selected = cv.get("est_selectionne") == "oui"
                    title = cv["filename"]
                    if selected:
                        title = f"{title} - selectionne"

                    st.write(f"**{title}**")
                    left, right = st.columns(2)
                    with left:
                        if not selected and st.button("Utiliser pour mes candidatures", key=f"select_cv_{cv['id']}"):
                            api_status, api_payload = request_api("POST", f"/cv/{cv['id']}/select")
                            if api_status == 200:
                                st.success("CV selectionne.")
                                st.rerun()
                            else:
                                st.error(api_payload.get("error", "Selection impossible"))
                    with right:
                        if st.button("Supprimer cette extraction", key=f"delete_cv_{cv['id']}"):
                            api_status, api_payload = request_api("DELETE", f"/cv/{cv['id']}")
                            if api_status == 200:
                                st.success("CV supprime.")
                                st.rerun()
                            else:
                                st.error(api_payload.get("error", "Suppression impossible"))

                    for chunk in cv["chunks"]:
                        label = cv_expander_label(cv["filename"], chunk["type_section"])
                        with st.expander(label):
                            st.write(chunk["contenu"])
        else:
            st.error(payload.get("error", "Impossible de charger les CV"))

    with offers_tab:
        st.subheader("Offres disponibles")
        status, payload = request_api("GET", "/offres")
        if status == 200:
            offres = payload.get("offres", [])
            if not offres:
                st.info("Aucune offre disponible pour le moment.")
            for offre in offres:
                with st.container(border=True):
                    st.markdown(f"**{offre['titre']}**")
                    meta = " · ".join(
                        valeur
                        for valeur in [
                            offre.get("domaine"),
                            offre.get("type_contrat"),
                            offre.get("duree_contrat"),
                        ]
                        if valeur
                    )
                    if meta:
                        st.caption(meta)
                    if offre.get("description_entreprise"):
                        st.write(offre["description_entreprise"])
                    st.write(offre["description"])
                    if offre.get("competences"):
                        st.caption(f"Competences : {offre['competences']}")
                    if st.button("Postuler", key=f"postuler_{offre['id']}", use_container_width=True):
                        ap_status, ap_payload = request_api(
                            "POST", "/candidatures", json={"offre_id": offre["id"]}
                        )
                        if ap_status == 201:
                            st.success("Candidature envoyee.")
                        else:
                            st.error(ap_payload.get("error", "Candidature impossible"))
        else:
            st.error(payload.get("error", "Impossible de charger les offres"))
        st.divider()
        st.caption("Le matching CV vers offres sera ajoute après les embeddings.")

    with applications_tab:
        st.subheader("Mes candidatures")
        status, payload = request_api("GET", "/candidatures/mine")
        if status == 200:
            candidatures = payload.get("candidatures", [])
            if not candidatures:
                st.info("Vous n'avez pas encore postule a une offre.")
            for candidature in candidatures:
                with st.container(border=True):
                    st.markdown(f"**{candidature.get('offre_titre') or 'Offre'}**")
                    st.caption(f"Statut : {candidature['statut']}")
        else:
            st.error(payload.get("error", "Impossible de charger vos candidatures"))

    with recruiter_request_tab:
        st.subheader("Demande d'évolution vers compte recruteur")
        status = user.get("statut_demande_recruteur", "aucune")
        if status == "aucune":
            st.write("Le compte est actuellement candidat. Une demande peut etre envoyee a l'administrateur.")
            with st.form("recruiter_request_form"):
                entreprise = st.text_input("Nom de l'entreprise")
                referent_rh = st.text_input("Referent RH")
                submitted = st.form_submit_button("Demander les droits recruteur", use_container_width=True)

            if submitted:
                api_status, payload = request_api(
                    "POST",
                    "/auth/request-recruiter-role",
                    json={
                        "entreprise": entreprise,
                        "referent_rh": referent_rh,
                    },
                )
                if api_status == 200:
                    set_user(payload["user"])
                    st.rerun()
                else:
                    st.error(payload.get("error", "Demande impossible"))
        elif status == "en_attente":
            st.warning("Demande recruteur en attente de validation administrateur.")
            if user.get("entreprise_demande_recruteur"):
                st.write(f"Entreprise : {user['entreprise_demande_recruteur']}")
            if user.get("referent_rh_demande_recruteur"):
                st.write(f"Referent RH : {user['referent_rh_demande_recruteur']}")
        elif status == "refusee":
            st.error("Demande recruteur refusée.")
        else:
            st.success("Demande recruteur approuvée.")

    with chatbot_tab:
        st.subheader("Copilote candidat")
        st.chat_input("Poser une question au copilote", disabled=True)
        st.info("Le copilote LLM sera branche apres le module IA.")


@st.dialog("CV du candidat", width="large")
def afficher_cv_dialog(candidature_id):
    cv_status, cv_payload = request_api("GET", f"/candidatures/{candidature_id}/cv")
    if cv_status == 200 and cv_payload.get("cv"):
        for chunk in cv_payload["cv"]["chunks"]:
            st.markdown(f"**{chunk['type_section']}**")
            st.write(chunk["contenu"])
    elif cv_status == 200:
        st.info("Ce candidat n'a pas encore depose de CV.")
    else:
        st.error(cv_payload.get("error", "CV indisponible"))


def recruiter_dashboard(user):
    dashboard_header(user)

    feedback = st.session_state.pop("candidature_feedback", None)
    if feedback:
        st.toast(feedback)

    offers_tab, search_tab, matching_tab, chatbot_tab = st.tabs(
        ["Offres", "Recherche", "Matching", "Copilote"]
    )

    with offers_tab:
        st.subheader("Publier une offre")
        with st.form("offer_form", clear_on_submit=True):
            titre = st.text_input("Nom du poste")
            type_contrat = st.selectbox(
                "Type de contrat",
                ["CDI", "CDD", "Stage", "Alternance", "Freelance", "Interim"],
            )
            duree_contrat = st.text_input("Duree du contrat (ex : 6 mois, indetermine)")
            domaine = st.text_input("Domaine (ex : Data, Developpement web)")
            competences = st.text_area("Competences requises (separees par des virgules)")
            description_entreprise = st.text_area("Description de l'entreprise")
            description = st.text_area("Description des missions")
            submitted = st.form_submit_button("Publier", use_container_width=True)

        if submitted:
            status, payload = request_api(
                "POST",
                "/offres",
                json={
                    "titre": titre,
                    "type_contrat": type_contrat,
                    "duree_contrat": duree_contrat,
                    "domaine": domaine,
                    "competences": competences,
                    "description_entreprise": description_entreprise,
                    "description": description,
                },
            )
            if status == 201:
                st.success("Offre publiee.")
                st.rerun()
            else:
                st.error(payload.get("error", "Publication impossible"))

        st.divider()
        st.subheader("Mes offres publiees")
        status, payload = request_api("GET", "/offres/mine")
        if status == 200:
            offres = payload.get("offres", [])
            if not offres:
                st.info("Aucune offre publiee pour le moment.")
            for offre in offres:
                label = f"{offre['titre']} - {offre.get('type_contrat') or ''}"
                with st.expander(label):
                    st.write(f"**Domaine** : {offre.get('domaine') or '-'}")
                    st.write(f"**Duree** : {offre.get('duree_contrat') or '-'}")
                    st.write(f"**Competences** : {offre.get('competences') or '-'}")
                    if offre.get("description_entreprise"):
                        st.write(f"**Entreprise** : {offre['description_entreprise']}")
                    st.write(f"**Missions** : {offre.get('description') or '-'}")

                    st.divider()
                    st.markdown("**Candidatures reçues**")
                    cand_status, cand_payload = request_api(
                        "GET", f"/candidatures/offre/{offre['id']}"
                    )
                    if cand_status == 200:
                        candidatures = cand_payload.get("candidatures", [])
                        if not candidatures:
                            st.caption("Aucune candidature pour le moment.")
                        statut_affichage = {
                            "deposee": ":grey[En attente]",
                            "acceptee": ":green[Acceptée]",
                            "refusee": ":red[Refusée]",
                        }
                        for candidature in candidatures:
                            statut = candidature["statut"]
                            nom = candidature.get("candidat_nom") or "Le candidat"
                            st.markdown(
                                f"**{nom}** ({candidature.get('candidat_email') or '-'}) — "
                                f"{statut_affichage.get(statut, statut)}"
                            )
                            col_cv, col_acc, col_ref = st.columns(3)
                            if col_cv.button(
                                "Voir le CV",
                                key=f"cv_{candidature['id']}",
                                use_container_width=True,
                            ):
                                afficher_cv_dialog(candidature["id"])
                            if col_acc.button(
                                "Accepter",
                                key=f"acc_{candidature['id']}",
                                use_container_width=True,
                                type="primary",
                                disabled=(statut == "acceptee"),
                            ):
                                r_status, r_payload = request_api(
                                    "POST",
                                    f"/candidatures/{candidature['id']}/statut",
                                    json={"statut": "acceptee"},
                                )
                                if r_status == 200:
                                    st.session_state["candidature_feedback"] = f"{nom} accepté(e)"
                                else:
                                    st.session_state["candidature_feedback"] = r_payload.get("error", "Erreur")
                                st.rerun()
                            if col_ref.button(
                                "Refuser",
                                key=f"ref_{candidature['id']}",
                                use_container_width=True,
                                disabled=(statut == "refusee"),
                            ):
                                r_status, r_payload = request_api(
                                    "POST",
                                    f"/candidatures/{candidature['id']}/statut",
                                    json={"statut": "refusee"},
                                )
                                if r_status == 200:
                                    st.session_state["candidature_feedback"] = f"{nom} refusé(e)"
                                else:
                                    st.session_state["candidature_feedback"] = r_payload.get("error", "Erreur")
                                st.rerun()
                            st.divider()
                    else:
                        st.caption(
                            cand_payload.get("error", "Impossible de charger les candidatures")
                        )
        else:
            st.error(payload.get("error", "Impossible de charger les offres"))

    with search_tab:
        st.subheader("Recherche de candidats")
        st.text_input("Requete libre", disabled=True)
        st.info("La recherche par embeddings sera ajoutee avec FAISS.")

    with matching_tab:
        st.subheader("Candidats classes par score")
        st.info("Le classement par similarite cosinus sera ajoute avec le moteur IA.")

    with chatbot_tab:
        st.subheader("Copilote RH")
        st.chat_input("Affiner une recherche de candidats", disabled=True)
        st.info("Le LLM expliquera les resultats lorsque le matching sera disponible.")


def admin_dashboard(user):
    dashboard_header(user)
    st.subheader("Demandes de comptes recruteurs")

    status, payload = request_api("GET", "/admin/recruiter-requests")
    if status != 200:
        st.error(payload.get("error", "Impossible de charger les demandes"))
        return

    requests_list = payload.get("requests", [])
    if not requests_list:
        st.info("Aucune demande recruteur en attente.")
        return

    for request_item in requests_list:
        with st.container(border=True):
            st.write(f"{request_item['nom']} - {request_item['email']}")
            st.write(f"Entreprise : {request_item.get('entreprise_demande_recruteur') or 'Non renseignee'}")
            st.write(f"Referent RH : {request_item.get('referent_rh_demande_recruteur') or 'Non renseigne'}")
            with st.form(f"grant_recruiter_{request_item['id']}"):
                entreprise = st.text_input(
                    "Entreprise",
                    value=request_item.get("entreprise_demande_recruteur") or "",
                    key=f"enterprise_{request_item['id']}",
                )
                submitted = st.form_submit_button("Donner les droits recruteur")
            if submitted:
                api_status, api_payload = request_api(
                    "POST",
                    f"/admin/users/{request_item['id']}/grant-recruiter",
                    json={"entreprise": entreprise},
                )
                if api_status == 200:
                    st.success("Droits recruteur accordes")
                    st.rerun()
                else:
                    st.error(api_payload.get("error", "Validation impossible"))


def main():
    show_api_status()

    user = get_user()
    if not user:
        auth_view()
        return

    if user["role"] == "candidat":
        candidate_dashboard(user)
    elif user["role"] == "recruteur":
        recruiter_dashboard(user)
    elif user["role"] == "administrateur":
        admin_dashboard(user)
    else:
        st.error("Role utilisateur inconnu")


if __name__ == "__main__":
    main()
