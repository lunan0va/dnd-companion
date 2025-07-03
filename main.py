"""
Haupt-Einstiegspunkt für die D&D Companion FastAPI-Anwendung.

Dieses Modul initialisiert die FastAPI-App, konfiguriert Metadaten wie Titel
und Beschreibung, richtet Startup-Events ein und bindet alle API-Router
aus den entsprechenden Modulen ein.
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from database import create_db_tables
from routes import users, characters, spells, items

@asynccontextmanager
async def lifespan(app: FastAPI):  # pylint: disable=unused-argument, redefined-outer-name
    """
    Verwaltet Startup- und Shutdown-Events der Anwendung.
    Beim Start werden die Datenbanktabellen erstellt.
    """
    print("Anwendung startet: Erstelle Datenbank-Tabellen, falls nötig...")
    create_db_tables()
    yield
    print("Anwendung wird heruntergefahren.")


app = FastAPI(
    title="D&D Companion API",
    description="Eine API zur Verwaltung von Dungeons & Dragons Charakteren, "
                "Zaubern und Gegenständen.",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(users.router, tags=["Benutzer"])
app.include_router(characters.router, tags=["Charaktere"])
app.include_router(spells.router, tags=["Zauber"])
app.include_router(items.router, tags=["Gegenstände"])
