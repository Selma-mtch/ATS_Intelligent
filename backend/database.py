from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from config import DATABASE_URL


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    return SessionLocal()


def init_db():
    import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    migrate_sqlite_schema()


def migrate_sqlite_schema():
    if not DATABASE_URL.startswith("sqlite"):
        return

    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    statements = []
    
    if "users" in table_names:
        columns = {column["name"] for column in inspector.get_columns("users")}

      if "demande_role_recruteur" not in columns:
          statements.append(
              "ALTER TABLE users ADD COLUMN demande_role_recruteur VARCHAR(10) NOT NULL DEFAULT 'non'"
          )
      if "statut_demande_recruteur" not in columns:
          statements.append(
              "ALTER TABLE users ADD COLUMN statut_demande_recruteur VARCHAR(30) NOT NULL DEFAULT 'aucune'"
          )
      if "entreprise_demande_recruteur" not in columns:
          statements.append(
              "ALTER TABLE users ADD COLUMN entreprise_demande_recruteur VARCHAR(160)"
          )
      if "referent_rh_demande_recruteur" not in columns:
          statements.append(
              "ALTER TABLE users ADD COLUMN referent_rh_demande_recruteur VARCHAR(160)"
          )

    if "offres" in table_names:
        offre_columns = {column["name"] for column in inspector.get_columns("offres")}
        for column_name, ddl in (
            ("type_contrat", "ALTER TABLE offres ADD COLUMN type_contrat VARCHAR(60)"),
            ("duree_contrat", "ALTER TABLE offres ADD COLUMN duree_contrat VARCHAR(80)"),
            ("domaine", "ALTER TABLE offres ADD COLUMN domaine VARCHAR(120)"),
            ("description_entreprise", "ALTER TABLE offres ADD COLUMN description_entreprise TEXT"),
        ):
            if column_name not in offre_columns:
                statements.append(ddl)

    if not statements:
        return

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
