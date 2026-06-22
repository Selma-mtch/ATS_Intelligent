import os
from datetime import datetime

import requests
import streamlit as st


API_URL = os.getenv("ATS_API_URL", "http://localhost:5001").rstrip("/")

st.set_page_config(
    page_title="ATS Intelligent",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

html, body, [class*="st-"] {
    font-family: 'Inter', sans-serif;
}

/* Header bar */
header[data-testid="stHeader"] {
    background: linear-gradient(90deg, #1a1a2e 0%, #16213e 100%);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
    color: white;
}
section[data-testid="stSidebar"] .stMarkdown p,
section[data-testid="stSidebar"] .stMarkdown h1,
section[data-testid="stSidebar"] .stMarkdown h2,
section[data-testid="stSidebar"] .stMarkdown h3 {
    color: white;
}

/* Cards */
div[data-testid="stExpander"],
div.stForm {
    border: 1px solid #e0e0e0;
    border-radius: 12px;
    padding: 4px;
}

/* Tabs */
button[data-baseweb="tab"] {
    font-weight: 600;
    font-size: 0.95rem;
}

/* Metric cards */
div[data-testid="stMetric"] {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 16px 20px;
    border-radius: 12px;
    color: white;
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
}
div[data-testid="stMetric"] label,
div[data-testid="stMetric"] [data-testid="stMetricValue"],
div[data-testid="stMetric"] [data-testid="stMetricLabel"] {
    color: white !important;
}

/* Buttons */
button[kind="primary"],
button[kind="secondary"] {
    border-radius: 8px;
    font-weight: 600;
    transition: all 0.2s;
}

/* Status badges */
.status-deposee { color: #3498db; font-weight: 600; }
.status-vue { color: #f39c12; font-weight: 600; }
.status-entretien { color: #9b59b6; font-weight: 600; }
.status-acceptee { color: #27ae60; font-weight: 600; }
.status-refusee { color: #e74c3c; font-weight: 600; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ── API helpers ──────────────────────────────────────────────────────────────

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
            payload = {"error": "Route API introuvable."}
        else:
            payload = {"error": response.text or "Reponse API illisible"}
    return response.status_code, payload


def upload_api(path, files):
    response = api_session().post(f"{API_URL}{path}", files=files, timeout=30)
    try:
        payload = response.json()
    except ValueError:
        payload = {"error": response.text or "Reponse API illisible"}
    return response.status_code, payload


def set_user(user):
    st.session_state.user = user


def get_user():
    return st.session_state.get("user")


def logout():
    request_api("POST", "/auth/logout")
    st.session_state.pop("user", None)


def format_date(iso_str):
    if not iso_str:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%d/%m/%Y %H:%M")
    except (ValueError, TypeError):
        return iso_str


STATUT_LABELS = {
    "deposee": "\U0001F4E9 Deposee",
    "vue": "\U0001F440 Vue",
    "entretien": "\U0001F4C5 Entretien",
    "acceptee": "✅ Acceptee",
    "refusee": "❌ Refusee",
}


# ── Sidebar ──────────────────────────────────────────────────────────────────

def show_sidebar():
    with st.sidebar:
        st.markdown("## ✨ ATS Intelligent")
        st.markdown("---")

        try:
            status, payload = request_api("GET", "/")
            if status == 200:
                st.success("⚡ API en ligne")
            else:
                st.warning("⚠️ API indisponible")
        except requests.RequestException:
            st.error("❌ Backend non joignable")

        user = get_user()
        if user:
            st.markdown("---")
            st.markdown(f"### \U0001F464 {user['nom']}")
            role_icons = {
                "candidat": "\U0001F393",
                "recruteur": "\U0001F4BC",
                "administrateur": "\U0001F6E1️",
            }
            icon = role_icons.get(user["role"], "")
            st.markdown(f"{icon} **{user['role'].capitalize()}**")
            st.markdown("---")
            st.button("\U0001F6AA Se deconnecter", on_click=logout, use_container_width=True)


# ── Auth view ────────────────────────────────────────────────────────────────

def auth_view():
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("# ✨ ATS Intelligent")
        st.markdown("##### Plateforme de recrutement intelligente avec IA")
        st.markdown("")

        mode = st.radio(
            "Mode",
            ["\U0001F511 Connexion", "\U0001F4DD Inscription"],
            horizontal=True,
            label_visibility="collapsed",
        )

        if "Connexion" in mode:
            with st.form("login_form", clear_on_submit=False):
                st.markdown("### Se connecter")
                email = st.text_input("\U0001F4E7 Email")
                password = st.text_input("\U0001F512 Mot de passe", type="password")
                submitted = st.form_submit_button(
                    "\U0001F680 Se connecter", use_container_width=True
                )

            if submitted:
                if not email or not password:
                    st.error("Veuillez remplir tous les champs.")
                else:
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

        if "Inscription" in mode:
            st.info(
                "\U0001F4A1 Les comptes sont crees comme candidats. "
                "Le role recruteur se demande depuis l'espace utilisateur."
            )
            with st.form("register_form", clear_on_submit=False):
                st.markdown("### Creer un compte")
                nom = st.text_input("\U0001F464 Nom complet", key="register_nom")
                email = st.text_input("\U0001F4E7 Email", key="register_email")
                password = st.text_input(
                    "\U0001F512 Mot de passe (min. 6 caracteres)",
                    type="password",
                    key="register_password",
                )
                submitted = st.form_submit_button(
                    "✅ Creer mon compte", use_container_width=True
                )

            if submitted:
                if not nom or not email or not password:
                    st.error("Veuillez remplir tous les champs.")
                else:
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


# ── Dashboard header ─────────────────────────────────────────────────────────

def dashboard_header(user):
    role_icons = {
        "candidat": "\U0001F393",
        "recruteur": "\U0001F4BC",
        "administrateur": "\U0001F6E1️",
    }
    icon = role_icons.get(user["role"], "✨")
    st.markdown(f"# {icon} Espace {user['role'].capitalize()}")
    st.markdown(f"Bienvenue, **{user['nom']}**")
    st.markdown("---")


# ══════════════════════════════════════════════════════════════════════════════
# CANDIDAT DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

def candidate_dashboard(user):
    dashboard_header(user)

    cv_tab, offers_tab, applications_tab, rh_tab = st.tabs(
        ["\U0001F4C4 Mon CV", "\U0001F4CB Offres", "\U0001F4E8 Candidatures", "\U0001F4DD Demande RH"]
    )

    with cv_tab:
        candidate_cv_tab(user)

    with offers_tab:
        candidate_offers_tab(user)

    with applications_tab:
        candidate_applications_tab(user)

    with rh_tab:
        candidate_rh_request_tab(user)


def candidate_cv_tab(user):
    st.subheader("\U0001F4C4 Mon CV")

    status, payload = request_api("GET", "/cv")
    cv = payload.get("cv") if status == 200 else None

    if cv:
        st.success(f"✅ CV depose le {format_date(cv['date_upload'])}")
        if cv.get("texte_extrait"):
            with st.expander("\U0001F50D Texte extrait du CV"):
                st.text(cv["texte_extrait"][:2000])
        st.markdown("---")
        st.markdown("**Remplacer le CV :**")

    uploaded_file = st.file_uploader(
        "Deposer un CV au format PDF",
        type=["pdf"],
        help="Taille maximale : 10 Mo",
    )

    if uploaded_file is not None:
        if st.button("\U0001F4E4 Envoyer le CV", use_container_width=True):
            with st.spinner("Upload en cours..."):
                api_status, api_payload = upload_api(
                    "/cv/upload",
                    files={"fichier": (uploaded_file.name, uploaded_file, "application/pdf")},
                )
            if api_status == 201:
                st.success("✅ CV depose avec succes !")
                st.rerun()
            else:
                st.error(api_payload.get("error", "Erreur lors de l'upload"))


def candidate_offers_tab(user):
    st.subheader("\U0001F4CB Offres disponibles")

    status, payload = request_api("GET", "/offres")
    if status != 200:
        st.error("Impossible de charger les offres.")
        return

    offres = payload.get("offres", [])
    if not offres:
        st.info("\U0001F4AD Aucune offre disponible pour le moment.")
        return

    search = st.text_input("\U0001F50E Rechercher une offre", placeholder="Titre, competences...")
    if search:
        search_lower = search.lower()
        offres = [
            o for o in offres
            if search_lower in o["titre"].lower()
            or search_lower in (o.get("competences") or "").lower()
            or search_lower in (o.get("description") or "").lower()
        ]

    for offre in offres:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {offre['titre']}")
                st.markdown(
                    f"\U0001F3E2 **{offre.get('entreprise', '—')}** · "
                    f"Publiee par {offre.get('recruteur_nom', '—')} · "
                    f"{format_date(offre.get('date_publication'))}"
                )
                st.markdown(offre["description"][:300])
                if offre.get("competences"):
                    skills = [s.strip() for s in offre["competences"].split(",")]
                    st.markdown(" ".join(f"`{s}`" for s in skills if s))
            with col2:
                st.markdown("")
                st.markdown("")
                if st.button(
                    "\U0001F680 Postuler",
                    key=f"apply_{offre['id']}",
                    use_container_width=True,
                ):
                    api_status, api_payload = request_api(
                        "POST",
                        "/candidatures",
                        json={"offre_id": offre["id"]},
                    )
                    if api_status == 201:
                        st.success("Candidature deposee !")
                        st.rerun()
                    else:
                        st.error(api_payload.get("error", "Erreur"))


def candidate_applications_tab(user):
    st.subheader("\U0001F4E8 Mes candidatures")

    status, payload = request_api("GET", "/candidatures")
    if status != 200:
        st.error("Impossible de charger les candidatures.")
        return

    candidatures = payload.get("candidatures", [])
    if not candidatures:
        st.info("\U0001F4AD Aucune candidature pour le moment. Consultez les offres et postulez !")
        return

    for c in candidatures:
        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**{c.get('offre_titre', 'Offre')}**")
                st.caption(f"\U0001F3E2 {c.get('entreprise', '—')}")
            with col2:
                label = STATUT_LABELS.get(c["statut"], c["statut"])
                st.markdown(f"**Statut :** {label}")
            with col3:
                st.caption(format_date(c.get("date_postulation")))


def candidate_rh_request_tab(user):
    st.subheader("\U0001F4DD Demande de role recruteur")

    statut = user.get("statut_demande_recruteur", "aucune")

    if statut == "aucune":
        st.markdown(
            "Vous etes actuellement **candidat**. Si vous etes un professionnel RH, "
            "vous pouvez demander les droits recruteur a l'administrateur."
        )
        if st.button("\U0001F4E9 Demander les droits recruteur", use_container_width=True):
            api_status, payload = request_api("POST", "/auth/request-recruiter-role")
            if api_status == 200:
                set_user(payload["user"])
                st.rerun()
            else:
                st.error(payload.get("error", "Demande impossible"))
    elif statut == "en_attente":
        st.warning("⏳ Votre demande est en attente de validation par l'administrateur.")
    elif statut == "refusee":
        st.error("❌ Votre demande a ete refusee par l'administrateur.")
    else:
        st.success("✅ Votre demande a ete approuvee !")


# ══════════════════════════════════════════════════════════════════════════════
# RECRUTEUR DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

def recruiter_dashboard(user):
    dashboard_header(user)

    offers_tab, candidates_tab = st.tabs(
        ["\U0001F4CB Mes offres", "\U0001F465 Candidats"]
    )

    with offers_tab:
        recruiter_offers_tab(user)

    with candidates_tab:
        recruiter_candidates_tab(user)


def recruiter_offers_tab(user):
    st.subheader("\U0001F4CB Gestion des offres")

    with st.expander("➕ Publier une nouvelle offre", expanded=False):
        with st.form("create_offer_form", clear_on_submit=True):
            titre = st.text_input("Titre du poste *")
            description = st.text_area("Description du poste *", height=150)
            competences = st.text_input(
                "Competences requises",
                placeholder="Python, SQL, Machine Learning...",
                help="Separer par des virgules",
            )
            submitted = st.form_submit_button(
                "\U0001F680 Publier l'offre", use_container_width=True
            )

        if submitted:
            if not titre or not description:
                st.error("Titre et description sont requis.")
            else:
                api_status, api_payload = request_api(
                    "POST",
                    "/offres",
                    json={
                        "titre": titre,
                        "description": description,
                        "competences": competences,
                    },
                )
                if api_status == 201:
                    st.success("✅ Offre publiee avec succes !")
                    st.rerun()
                else:
                    st.error(api_payload.get("error", "Erreur"))

    st.markdown("---")
    st.markdown("### Mes offres publiees")

    status, payload = request_api("GET", "/offres/mes-offres")
    if status != 200:
        st.error("Impossible de charger les offres.")
        return

    offres = payload.get("offres", [])
    if not offres:
        st.info("\U0001F4AD Aucune offre publiee. Creez votre premiere offre ci-dessus !")
        return

    for offre in offres:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"### {offre['titre']}")
                st.caption(f"Publiee le {format_date(offre.get('date_publication'))}")
                st.markdown(offre["description"][:200])
                if offre.get("competences"):
                    skills = [s.strip() for s in offre["competences"].split(",")]
                    st.markdown(" ".join(f"`{s}`" for s in skills if s))
            with col2:
                st.markdown("")
                if st.button(
                    "\U0001F5D1️ Supprimer",
                    key=f"del_offre_{offre['id']}",
                    use_container_width=True,
                ):
                    api_status, _ = request_api("DELETE", f"/offres/{offre['id']}")
                    if api_status == 200:
                        st.rerun()
                    else:
                        st.error("Erreur lors de la suppression")


def recruiter_candidates_tab(user):
    st.subheader("\U0001F465 Candidatures recues")

    status, payload = request_api("GET", "/offres/mes-offres")
    if status != 200:
        st.error("Impossible de charger les offres.")
        return

    offres = payload.get("offres", [])
    if not offres:
        st.info("Publiez d'abord une offre pour recevoir des candidatures.")
        return

    selected_offre = st.selectbox(
        "Selectionner une offre",
        offres,
        format_func=lambda o: o["titre"],
    )

    if selected_offre:
        c_status, c_payload = request_api(
            "GET", f"/candidatures/offre/{selected_offre['id']}"
        )
        if c_status != 200:
            st.error("Impossible de charger les candidatures.")
            return

        candidatures = c_payload.get("candidatures", [])
        if not candidatures:
            st.info("Aucune candidature pour cette offre.")
            return

        st.markdown(f"**{len(candidatures)} candidature(s)**")

        for c in candidatures:
            with st.container(border=True):
                col1, col2, col3 = st.columns([2, 1, 1])
                with col1:
                    st.markdown(f"**{c.get('candidat_nom', '—')}**")
                    st.caption(c.get("candidat_email", ""))
                with col2:
                    label = STATUT_LABELS.get(c["statut"], c["statut"])
                    st.markdown(f"**{label}**")
                with col3:
                    new_statut = st.selectbox(
                        "Changer statut",
                        ["deposee", "vue", "entretien", "acceptee", "refusee"],
                        index=["deposee", "vue", "entretien", "acceptee", "refusee"].index(c["statut"])
                        if c["statut"] in ["deposee", "vue", "entretien", "acceptee", "refusee"]
                        else 0,
                        key=f"statut_{c['id']}",
                        label_visibility="collapsed",
                    )
                    if new_statut != c["statut"]:
                        if st.button("✅", key=f"update_{c['id']}"):
                            request_api(
                                "PUT",
                                f"/candidatures/{c['id']}/statut",
                                json={"statut": new_statut},
                            )
                            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
# ADMIN DASHBOARD
# ══════════════════════════════════════════════════════════════════════════════

def admin_dashboard(user):
    dashboard_header(user)

    stats_tab, requests_tab, users_tab = st.tabs(
        ["\U0001F4CA Tableau de bord", "\U0001F4DD Demandes recruteur", "\U0001F465 Utilisateurs"]
    )

    with stats_tab:
        admin_stats_tab()

    with requests_tab:
        admin_requests_tab()

    with users_tab:
        admin_users_tab()


def admin_stats_tab():
    st.subheader("\U0001F4CA Statistiques")

    status, payload = request_api("GET", "/admin/stats")
    if status != 200:
        st.error("Impossible de charger les statistiques.")
        return

    stats = payload.get("stats", {})

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("\U0001F465 Utilisateurs", stats.get("total_utilisateurs", 0))
    col2.metric("\U0001F4CB Offres", stats.get("total_offres", 0))
    col3.metric("\U0001F4E8 Candidatures", stats.get("total_candidatures", 0))
    col4.metric("\U0001F4C4 CVs deposes", stats.get("total_cvs", 0))

    st.markdown("---")

    col5, col6, col7 = st.columns(3)
    col5.metric("\U0001F393 Candidats", stats.get("total_candidats", 0))
    col6.metric("\U0001F4BC Recruteurs", stats.get("total_recruteurs", 0))
    col7.metric("⏳ Demandes en attente", stats.get("demandes_en_attente", 0))


def admin_requests_tab():
    st.subheader("\U0001F4DD Demandes de comptes recruteurs")

    status, payload = request_api("GET", "/admin/recruiter-requests")
    if status != 200:
        st.error(payload.get("error", "Impossible de charger les demandes"))
        return

    requests_list = payload.get("requests", [])
    if not requests_list:
        st.info("✅ Aucune demande en attente.")
        return

    st.markdown(f"**{len(requests_list)} demande(s) en attente**")

    for req in requests_list:
        with st.container(border=True):
            col1, col2 = st.columns([2, 1])
            with col1:
                st.markdown(f"### {req['nom']}")
                st.caption(f"\U0001F4E7 {req['email']}")
            with col2:
                with st.form(f"grant_{req['id']}"):
                    entreprise = st.text_input(
                        "Entreprise",
                        key=f"ent_{req['id']}",
                        placeholder="Nom de l'entreprise",
                    )
                    c1, c2 = st.columns(2)
                    with c1:
                        approve = st.form_submit_button(
                            "✅ Approuver", use_container_width=True
                        )
                    with c2:
                        reject = st.form_submit_button(
                            "❌ Refuser", use_container_width=True
                        )

                if approve:
                    if not entreprise:
                        st.error("Entreprise requise pour approuver.")
                    else:
                        api_status, api_payload = request_api(
                            "POST",
                            f"/admin/users/{req['id']}/grant-recruiter",
                            json={"entreprise": entreprise},
                        )
                        if api_status == 200:
                            st.success("Droits recruteur accordes !")
                            st.rerun()
                        else:
                            st.error(api_payload.get("error", "Erreur"))

                if reject:
                    api_status, api_payload = request_api(
                        "POST", f"/admin/users/{req['id']}/reject-recruiter"
                    )
                    if api_status == 200:
                        st.success("Demande refusee.")
                        st.rerun()
                    else:
                        st.error(api_payload.get("error", "Erreur"))


def admin_users_tab():
    st.subheader("\U0001F465 Tous les utilisateurs")

    status, payload = request_api("GET", "/admin/users")
    if status != 200:
        st.error("Impossible de charger les utilisateurs.")
        return

    users = payload.get("users", [])
    if not users:
        st.info("Aucun utilisateur.")
        return

    role_icons = {
        "candidat": "\U0001F393",
        "recruteur": "\U0001F4BC",
        "administrateur": "\U0001F6E1️",
    }

    for u in users:
        icon = role_icons.get(u["role"], "")
        with st.container(border=True):
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**{u['nom']}**")
                st.caption(u["email"])
            with col2:
                st.markdown(f"{icon} {u['role'].capitalize()}")
            with col3:
                st.caption(f"Inscrit le {format_date(u.get('created_at'))}")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    show_sidebar()

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
