from fastapi import FastAPI

from database import create_db_tables, drop_db_tables
from routes import users, characters, spells, items

app = FastAPI(
    title="D&D Companion API",
    description="Eine API zur Verwaltung von Dungeons & Dragons Charakteren, Zaubern und Gegenständen.",
    version="0.0.1"
)

@app.on_event("startup")
def on_startup():
    #drop_db_tables()
    create_db_tables()

app.include_router(users.router, tags=["Benutzer"])
app.include_router(characters.router, tags=["Charaktere"])
app.include_router(spells.router, tags=["Zauber"])
app.include_router(items.router, tags=["Gegenstände"])