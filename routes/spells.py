"""
Definiert die API-Endpunkte für die Verwaltung von Zaubern (Spells).

Dieses Modul enthält Endpunkte zum Abrufen aller zwischengespeicherten Zauber,
zum Erstellen neuer Zauber durch Abfrage der externen D&D-API und zum Löschen.
"""
from typing import List

from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session

from database import get_db
from models import Spell
from models.schemas import SpellCreateRequest, SpellResponse, UserResponse
from repositories import spell_repo
from utils.errors import raise_api_error
from .users import get_current_user
from .helpers import get_or_create_api_object, APIObjectConfig

router = APIRouter()


def _get_spell_specific_fields(api_data: dict) -> dict:
    """Extrahiert die zusätzlichen, zauberspezifischen Felder aus der API-Antwort."""
    return {
        "level": api_data.get("level"),
        "casting_time": api_data.get("casting_time"),
        "spell_range": api_data.get("range"),
        "components": ", ".join(api_data.get("components", [])),
        "duration": api_data.get("duration"),
        "school": api_data.get("school", {}).get("name"),
    }


@router.get("/spells", response_model=List[SpellResponse], summary="Alle Zauber abrufen")
def get_all_spells(db: Session = Depends(get_db)):
    """Ruft eine Liste aller Zauber ab, die im System zwischengespeichert sind."""
    return spell_repo.get_all(db=db)


@router.get(
    "/spells/{spell_id}",
    response_model=SpellResponse,
    summary="Einen einzelnen Zauber anhand der ID abrufen",
)
def get_spell(spell_id: int, db: Session = Depends(get_db)):
    """Ruft einen einzelnen, zwischengespeicherten Zauber anhand seiner primären ID ab."""
    spell = spell_repo.get(db=db, obj_id=spell_id)
    if not spell:
        raise_api_error(404, "SPELL_NOT_FOUND", "Zauber nicht gefunden.")
    return spell


@router.post(
    "/spells",
    response_model=SpellResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Neuen Zauber aus der D&D-API erstellen und zwischenspeichern",
)
def create_spell_from_api(
    request: SpellCreateRequest,
    _current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Erstellt einen neuen Zauber, indem er von der D&D 5e API abgerufen wird.
    Die Logik ist in eine wiederverwendbare Hilfsfunktion ausgelagert.
    """
    config = APIObjectConfig(
        repo=spell_repo,
        model_class=Spell,
        api_endpoint="spells",
        extra_fields_factory=_get_spell_specific_fields,
    )
    return get_or_create_api_object(
        db=db,
        request_name=request.name,
        config=config,
    )


@router.delete(
    "/spells/{spell_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Einen Zauber löschen",
)
def delete_spell(
    spell_id: int,
    _current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Löscht einen zwischengespeicherten Zauber aus der Datenbank."""
    deleted_spell = spell_repo.delete(db=db, obj_id=spell_id)
    if not deleted_spell:
        raise_api_error(404, "SPELL_NOT_FOUND", "Zauber nicht gefunden.")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
