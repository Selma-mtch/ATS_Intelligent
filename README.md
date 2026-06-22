# ATS Intelligent

Projet de S6 en BUT 3 Informatique.

Le but est de faire une petite plateforme ATS pour mettre en relation des candidats et des recruteurs. Pour l'instant on a surtout pose la base du projet : backend Flask, base SQLite, inscription/connexion et interface Streamlit.

## Fonctionnement actuel

- un utilisateur cree un compte classique ;
- le compte est candidat par defaut ;
- si la personne est recruteur, elle fait une demande depuis son espace ;
- un administrateur accepte la demande ;
- le compte passe alors en recruteur.

La partie CV commence a etre disponible : on peut envoyer un PDF, extraire son texte et le decouper en sections. Les offres, le matching IA et le copilote ne sont pas encore branches.

## Technologies utilisees

- Flask pour l'API ;
- SQLite avec SQLAlchemy pour la base ;
- Streamlit pour l'interface ;
- sessions Flask pour rester connecte ;
- bcrypt pour ne pas stocker les mots de passe en clair.

## Structure

```text
backend/   API Flask et base de donnees
frontend/  interface Streamlit
ai/        futur code IA
data/      donnees de test
docs/      documents du projet
```

## Lancer le backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

API :

```text
http://localhost:5001
```

## Lancer le frontend

Dans un deuxieme terminal :

```powershell
cd frontend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\streamlit.exe run streamlit_app.py
```

Interface :

```text
http://localhost:8501
```

## Creer le premier admin

Une fois les dependances backend installees :

```powershell
cd backend
.\.venv\Scripts\python.exe create_admin.py
```

Compte cree par defaut :

```text
email: admin@ats.local
mot de passe: admin123
```

## Routes utiles

```text
POST /auth/register
POST /auth/login
POST /auth/logout
GET  /auth/me
POST /auth/request-recruiter-role
GET  /admin/recruiter-requests
POST /admin/users/<id>/grant-recruiter
POST /cv/upload
GET  /cv/me
POST /offres
GET  /offres/mine
```

## Pendant le developpement

La base SQLite est locale. Si on change les modeles et que la base ne correspond plus, on supprime simplement :

```text
backend/ats_intelligent.db
```

Puis on relance Flask. Les tables seront recreees.
