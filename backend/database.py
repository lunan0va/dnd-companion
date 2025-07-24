"""
Dieses Modul ist für die gesamte Datenbankkonfiguration und das Session-Management zuständig.

Es initialisiert die SQLAlchemy-Engine basierend auf der `DATABASE_URL` aus den
Umgebungsvariablen und stellt eine `SessionLocal`-Factory zur Verfügung, um
Datenbank-Sessions zu erstellen.

Die Hauptfunktion dieses Moduls ist die `get_db`-Abhängigkeit (Dependency),
die in FastAPI-Routen verwendet wird, um eine saubere und abgeschlossene
Datenbank-Session pro Anfrage zu gewährleisten.

Zusätzlich enthält es Hilfsfunktionen zum Erstellen (`create_db_tables`) und
Löschen (`drop_db_tables`) aller im `Base`-Metadaten-Objekt definierten Tabellen.
"""

import os
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from dotenv import load_dotenv

from models import Base

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_db_tables():
    """Erstellt alle Tabellen in der Datenbank, die von Base erben."""
    Base.metadata.create_all(bind=engine)


def drop_db_tables():
    """Löscht alle Tabellen in der Datenbank, die von Base erben."""
    Base.metadata.drop_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
    """
        FastAPI-Abhängigkeit, die eine Datenbank-Session für eine Anfrage bereitstellt.

        Stellt sicher, dass die Session nach Abschluss der Anfrage immer geschlossen wird.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
