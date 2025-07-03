"""
Haupt-Einstiegspunkt für die D&D Companion FastAPI-Anwendung.

Dieses Modul initialisiert die FastAPI-App, konfiguriert Metadaten wie Titel
und Beschreibung, richtet Startup-Events ein und bindet alle API-Router
aus den entsprechenden Modulen ein.
"""

from fastapi import FastAPI

from database import create_db_tables
from routes import users, characters, spells, items

app = FastAPI(
    title="D&D Companion API",
    description="Eine API zur Verwaltung von Dungeons & Dragons Charakteren, "
                "Zaubern und Gegenständen.",
    version="0.0.1"
)

@app.on_event("startup")
def on_startup():
    """
        Führt Aktionen beim Start der Anwendung aus.

        Stellt sicher, dass alle notwendigen Datenbanktabellen existieren,
        indem sie bei Bedarf erstellt werden.
    """
    create_db_tables()

app.include_router(users.router, tags=["Benutzer"])
app.include_router(characters.router, tags=["Charaktere"])
app.include_router(spells.router, tags=["Zauber"])
app.include_router(items.router, tags=["Gegenstände"])
