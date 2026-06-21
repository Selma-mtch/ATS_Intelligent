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
                st.rerun()
            else:
                st.error(payload.get("error", "Connexion impossible"))

    if mode == "Inscription":
        st.info("Tous les comptes sont crees comme candidats. Le role recruteur se demande ensuite depuis l'espace utilisateur.")
        with st.form("register_form", clear_on_submit=False):
            nom = st.text_input("Nom", key="register_nom")
            email = st.text_input("Email", key="register_email")
            password = st.text_input("Mot de passe", type="password", key="register_password")
            submitted = st.form_submit_button("Creer mon compte", use_container_width=True)

        if submitted:
            status, payload = request_api(
                "POST",
                "/auth/register",
                json={"nom": nom, "email": email, "mot_de_passe": password},
            )
            if status == 201:
                set_user(payload["user"])
                st.rerun()
            else:
                st.error(payload.get("error", "Inscription impossible"))


def dashboard_header(user):
    left, right = st.columns([0.78, 0.22])
    with left:
        st.title("ATS Intelligent")
        st.caption(f"{user['nom']} - {user['role']}")
    with right:
        st.button("Se deconnecter", on_click=logout, use_container_width=True)


def candidate_dashboard(user):
    dashboard_header(user)

    cv_tab, offers_tab, applications_tab, recruiter_request_tab, chatbot_tab = st.tabs(
        ["CV", "Offres", "Candidatures", "Demande RH", "Copilote"]
    )

    with cv_tab:
        st.subheader("Depot de CV PDF")
        st.file_uploader("CV au format PDF", type=["pdf"], disabled=True)
        st.info("La route backend d'upload CV sera ajoutee avec l'etape extraction PDF.")

    with offers_tab:
        st.subheader("Offres recommandees")
        st.info("Le matching CV vers offres sera ajoute apres les embeddings.")

    with applications_tab:
        st.subheader("Mes candidatures")
        st.info("La candidature en un clic sera ajoutee avec la gestion des offres.")

    with recruiter_request_tab:
        st.subheader("Demande d'evolution vers compte recruteur")
        status = user.get("statut_demande_recruteur", "aucune")
        if status == "aucune":
            st.write("Le compte est actuellement candidat. Une demande peut etre envoyee a l'administrateur.")
            if st.button("Demander les droits recruteur", use_container_width=True):
                api_status, payload = request_api("POST", "/auth/request-recruiter-role")
                if api_status == 200:
                    set_user(payload["user"])
                    st.rerun()
                else:
                    st.error(payload.get("error", "Demande impossible"))
        elif status == "en_attente":
            st.warning("Demande recruteur en attente de validation administrateur.")
        elif status == "refusee":
            st.error("Demande recruteur refusee.")
        else:
            st.success("Demande recruteur approuvee.")

    with chatbot_tab:
        st.subheader("Copilote candidat")
        st.chat_input("Poser une question au copilote", disabled=True)
        st.info("Le copilote LLM sera branche apres le module IA.")


def recruiter_dashboard(user):
    dashboard_header(user)

    offers_tab, search_tab, matching_tab, chatbot_tab = st.tabs(
        ["Offres", "Recherche", "Matching", "Copilote"]
    )

    with offers_tab:
        st.subheader("Publier une offre")
        with st.form("offer_preview_form"):
            st.text_input("Titre", disabled=True)
            st.text_area("Description", disabled=True)
            st.text_input("Competences", disabled=True)
            st.form_submit_button("Publier", disabled=True, use_container_width=True)
        st.info("Les routes backend des offres seront ajoutees dans l'etape gestion des offres.")

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
            with st.form(f"grant_recruiter_{request_item['id']}"):
                entreprise = st.text_input("Entreprise", key=f"enterprise_{request_item['id']}")
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
