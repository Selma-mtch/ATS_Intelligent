import bcrypt

from database import get_db, init_db
from models import Administrateur, User


EMAIL = "admin@ats.local"
PASSWORD = "admin123"


def main():
    init_db()
    db = get_db()

    existing_admin = db.query(User).filter_by(email=EMAIL).first()
    if existing_admin:
        print("Le compte admin existe deja.")
        print(f"Email: {EMAIL}")
        return

    password_hash = bcrypt.hashpw(PASSWORD.encode(), bcrypt.gensalt()).decode()
    admin = User(
        nom="Administrateur",
        email=EMAIL,
        mot_de_passe_hash=password_hash,
        role="administrateur",
    )

    db.add(admin)
    db.flush()
    db.add(Administrateur(user_id=admin.id))
    db.commit()
    db.close()

    print("Compte admin cree.")
    print(f"Email: {EMAIL}")
    print(f"Mot de passe: {PASSWORD}")


if __name__ == "__main__":
    main()
