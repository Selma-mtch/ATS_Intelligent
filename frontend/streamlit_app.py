import os

import requests
import streamlit as st


API_URL = os.getenv("ATS_API_URL", "http://localhost:5001").rstrip("/")


st.set_page_config(
    page_title="ATS Intelligent",
    page_icon="🎯",
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


def inject_css():
    st.markdown(
        """
        <style>
        /* Halos lumineux en fond de page */
        .stApp {
            background:
                radial-gradient(900px 520px at 100% -10%, rgba(99, 102, 241, 0.14), transparent 60%),
                radial-gradient(720px 420px at -10% 8%, rgba(139, 92, 246, 0.10), transparent 55%);
        }

        /* Conteneur principal centre, aere, avec animation d'entree */
        @keyframes fadeInUp {
            from {opacity: 0; transform: translateY(14px);}
            to {opacity: 1; transform: translateY(0);}
        }
        .block-container {
            padding-top: 2.5rem;
            padding-bottom: 3rem;
            max-width: 1080px;
            animation: fadeInUp .5s ease both;
        }

        /* Titre principal en degrade */
        h1 {
            font-weight: 800;
            letter-spacing: -0.7px;
            background: linear-gradient(90deg, #A5B4FC 0%, #6366F1 45%, #C4B5FD 100%);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        h2, h3 {font-weight: 700; letter-spacing: -0.2px;}

        /* Boutons : remplissage degrade indigo + survol anime */
        .stButton > button,
        .stFormSubmitButton > button,
        .stDownloadButton > button {
            background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
            color: #fff;
            border: none;
            border-radius: 10px;
            font-weight: 600;
            box-shadow: 0 2px 10px rgba(99, 102, 241, 0.25);
            transition: transform .12s ease, box-shadow .12s ease, filter .12s ease;
        }
        .stButton > button:hover,
        .stFormSubmitButton > button:hover,
        .stDownloadButton > button:hover {
            filter: brightness(1.08);
            box-shadow: 0 8px 22px rgba(99, 102, 241, 0.45);
            transform: translateY(-2px);
        }
        .stButton > button:active,
        .stFormSubmitButton > button:active {transform: translateY(0);}
        /* Boutons desactives : aspect neutre */
        .stButton > button:disabled,
        .stFormSubmitButton > button:disabled {
            background: rgba(255, 255, 255, 0.06);
            color: rgba(255, 255, 255, 0.4);
            box-shadow: none;
        }

        /* Formulaires et conteneurs en "cartes" avec survol */
        [data-testid="stForm"],
        [data-testid="stExpander"] {
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 16px;
            background: rgba(255, 255, 255, 0.02);
            transition: border-color .15s ease, box-shadow .15s ease, transform .15s ease;
        }
        [data-testid="stForm"] {padding: 1.4rem 1.4rem 0.4rem;}
        [data-testid="stForm"]:hover,
        [data-testid="stExpander"]:hover {
            border-color: rgba(99, 102, 241, 0.4);
            box-shadow: 0 8px 26px rgba(0, 0, 0, 0.25);
        }

        /* Champs de saisie arrondis + halo au focus */
        .stTextInput input,
        .stTextArea textarea,
        .stSelectbox div[data-baseweb="select"] > div {
            border-radius: 10px !important;
            transition: box-shadow .15s ease, border-color .15s ease;
        }
        .stTextInput input:focus,
        .stTextArea textarea:focus {
            box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.35) !important;
        }

        /* Onglets en pastilles, avec etat actif marque */
        .stTabs [data-baseweb="tab-list"] {gap: 6px;}
        .stTabs [data-baseweb="tab"] {
            border-radius: 10px;
            padding: 8px 18px;
            font-weight: 600;
            transition: background .15s ease, color .15s ease;
        }
        .stTabs [data-baseweb="tab"]:hover {background: rgba(99, 102, 241, 0.12);}
        .stTabs [aria-selected="true"] {
            background: rgba(99, 102, 241, 0.18);
            color: #C7D2FE !important;
        }

        /* Alertes arrondies */
        .stAlert {border-radius: 12px;}

        /* Barre laterale avec un degrade */
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #171A23 0%, #0E1117 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.06);
        }

        /* Bloc d'identite dans la sidebar */
        .ats-brand {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 6px 4px 16px;
            margin-bottom: 8px;
            border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }
        .ats-brand .logo {
            font-size: 26px;
            line-height: 1;
            filter: drop-shadow(0 2px 6px rgba(99, 102, 241, 0.5));
        }
        .ats-brand .name {
            font-weight: 800;
            font-size: 18px;
            background: linear-gradient(90deg, #A5B4FC, #C4B5FD);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Scrollbar discrete */
        ::-webkit-scrollbar {width: 10px; height: 10px;}
        ::-webkit-scrollbar-thumb {
            background: rgba(99, 102, 241, 0.4);
            border-radius: 8px;
        }
        ::-webkit-scrollbar-thumb:hover {background: rgba(99, 102, 241, 0.65);}

        /* Interface epuree : menu et pied de page masques */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        </style>
        """,
        unsafe_allow_html=True,
    )


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
                st.write("Sections trouvees :")
                for chunk in payload["chunks"]:
                    with st.expander(chunk["type_section"]):
                        st.write(chunk["contenu"])
            else:
                st.error(payload.get("error", "Upload impossible"))

        status, payload = request_api("GET", "/cv/me")
        if status == 200 and payload.get("cv"):
            st.divider()
            st.subheader("CV deja enregistre")
            for chunk in payload["cv"]["chunks"]:
                with st.expander(chunk["type_section"]):
                    st.write(chunk["contenu"])

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
    inject_css()
    st.sidebar.markdown(
        '<div class="ats-brand"><span class="logo">🎯</span>'
        '<span class="name">ATS Intelligent</span></div>',
        unsafe_allow_html=True,
    )
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
