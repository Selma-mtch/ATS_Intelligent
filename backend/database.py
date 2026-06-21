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
    if "users" not in inspector.get_table_names():
        return

    columns = {column["name"] for column in inspector.get_columns("users")}
    statements = []

    if "demande_role_recruteur" not in columns:
        statements.append(
            "ALTER TABLE users ADD COLUMN demande_role_recruteur VARCHAR(10) NOT NULL DEFAULT 'non'"
        )
    if "statut_demande_recruteur" not in columns:
        statements.append(
            "ALTER TABLE users ADD COLUMN statut_demande_recruteur VARCHAR(30) NOT NULL DEFAULT 'aucune'"
        )

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))
