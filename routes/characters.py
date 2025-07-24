"""
Definiert die API-Endpunkte für die Verwaltung von Charakteren.

Dieses Modul enthält alle CRUD-Operationen für Charaktere sowie Endpunkte
zum Hinzufügen und Entfernen von Zaubern und Items zu einem Charakter.
"""
from typing import List

from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session

from database import get_db
from models import Character, Spell, Item
from models.schemas import (
    CharacterCreate,
    CharacterUpdate,
    CharacterResponse,
    UserResponse,
)
from repositories import character_repo, spell_repo, item_repo
from utils.dnd_api_client import fetch_dnd_classes_from_api
from utils.errors import raise_api_error
from .users import get_current_user

router = APIRouter()

def get_spell_dependency(spell_id: int, db: Session = Depends(get_db)) -> Spell:
    """Dependency, die einen Zauber anhand der ID abruft."""
    spell = spell_repo.get(db, obj_id=spell_id)
    if not spell:
        raise_api_error(404, "SPELL_NOT_FOUND", "Zauber nicht gefunden.")
    return spell


def get_item_dependency(item_id: int, db: Session = Depends(get_db)) -> Item:
    """Dependency, die ein Item anhand der ID abruft."""
    item = item_repo.get(db, obj_id=item_id)
    if not item:
        raise_api_error(404, "ITEM_NOT_FOUND", "Item nicht gefunden.")
    return item


async def validate_game_class(gameclass: str):
    """
    Prüft, ob der übergebene Klassenname gültig ist, indem er mit der D&D-API abgeglichen wird.
    Wirft einen API-Fehler, wenn die Klasse ungültig ist.
    """
    valid_classes = await fetch_dnd_classes_from_api()
    if gameclass.lower() not in [cls.lower() for cls in valid_classes]:
        error_msg = f"Ungültiger Klassenname. Erlaubte Klassen sind: {', '.join(valid_classes)}"
        raise_api_error(400, "INVALID_CLASS_NAME", error_msg)


def get_character_for_user(
    character_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Character:
    """
    Dependency, die einen Charakter für den aktuellen Benutzer abruft.
    Stellt sicher, dass der Charakter existiert und dem Benutzer gehört.
    Wirft einen 404-Fehler, wenn nicht gefunden.
    """
    character = character_repo.get_by_id_and_user(
        db=db, character_id=character_id, user_id=current_user.id
    )
    if not character:
        raise_api_error(
            404, "CHARACTER_NOT_FOUND", "Charakter nicht gefunden oder gehört nicht zum Benutzer."
        )
    return character


@router.get(
    "/characters",
    response_model=List[CharacterResponse],
    summary="Alle Charaktere des aktuellen Benutzers abrufen",
)
def get_all_characters(
    current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)
):
    """Ruft eine Liste aller Charaktere ab, die dem eingeloggten Benutzer gehören."""
    return character_repo.get_all_for_user(db=db, user_id=current_user.id)


@router.get(
    "/characters/{character_id}",
    response_model=CharacterResponse,
    summary="Einen einzelnen Charakter anhand der ID abrufen",
)
def get_character(character: Character = Depends(get_character_for_user)):
    """
    Ruft einen spezifischen Charakter anhand seiner ID ab.
    Stellt sicher, dass der Charakter dem aktuellen Benutzer gehört.
    """
    return character


@router.post(
    "/characters",
    response_model=CharacterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Einen neuen Charakter erstellen",
)
async def create_character(
    char_create: CharacterCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Erstellt einen neuen Charakter für den aktuell eingeloggten Benutzer."""
    await validate_game_class(char_create.gameclass)
    return character_repo.create_for_user(
        db=db, obj_in=char_create, user_id=current_user.id
    )


@router.put(
    "/characters/{character_id}",
    response_model=CharacterResponse,
    summary="Einen bestehenden Charakter aktualisieren",
)
async def update_character(
    char_update: CharacterUpdate,
    character: Character = Depends(get_character_for_user),
    db: Session = Depends(get_db),
):
    """Aktualisiert die Daten eines bestehenden Charakters."""
    update_data = char_update.model_dump(exclude_unset=True)
    if "gameclass" in update_data:
        await validate_game_class(update_data["gameclass"])

    return character_repo.update(db=db, db_obj=character, obj_in=char_update)


@router.delete(
    "/characters/{character_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Einen Charakter löschen",
)
def delete_character(
    character: Character = Depends(get_character_for_user),
    db: Session = Depends(get_db),
):
    """Löscht einen Charakter anhand seiner ID."""
    character_repo.delete(db=db, db_obj=character)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/characters/{character_id}/spells/{spell_id}",
    response_model=CharacterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Einem Charakter einen Zauber hinzufügen",
)
def add_spell_to_character(
    character: Character = Depends(get_character_for_user),
    spell: Spell = Depends(get_spell_dependency),
    db: Session = Depends(get_db),
):
    """Fügt einen Zauber zur Zauberliste eines Charakters hinzu."""
    if spell in [cs.spell for cs in character.spells]:
        raise_api_error(
            409, "SPELL_ALREADY_EXISTS", "Zauber ist bereits mit dem Charakter verbunden."
        )

    character_repo.add_spell_to_character(db=db, character=character, spell_id=spell.id)

    db.refresh(character)
    return character


@router.delete(
    "/characters/{character_id}/spells/{spell_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Einen Zauber von einem Charakter entfernen",
)
def remove_spell_from_character(
    spell_id: int,
    character: Character = Depends(get_character_for_user),
    db: Session = Depends(get_db),
):
    """Entfernt die Verknüpfung zwischen einem Charakter und einem Zauber."""
    association = character_repo.get_spell_association(
        db, character_id=character.id, spell_id=spell_id
    )
    if not association:
        raise_api_error(
            404, "SPELL_NOT_FOUND", "Zauber nicht gefunden oder nicht mit Charakter verbunden."
        )

    character_repo.remove_spell_from_character(db=db, association=association)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/characters/{character_id}/items/{item_id}",
    response_model=CharacterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Einem Charakter ein Item hinzufügen",
)
def add_item_to_character(
    character: Character = Depends(get_character_for_user),
    item: Item = Depends(get_item_dependency),
    db: Session = Depends(get_db),
):
    """Fügt ein Item zum Inventar eines Charakters hinzu."""
    if item in [ci.item for ci in character.items]:
        raise_api_error(409, "ITEM_ALREADY_EXISTS", "Item ist bereits mit dem Charakter verbunden.")

    character_repo.add_item_to_character(db=db, character=character, item_id=item.id)

    db.refresh(character)
    return character


@router.delete(
    "/characters/{character_id}/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Ein Item von einem Charakter entfernen",
)
def remove_item_from_character(
    item_id: int,
    character: Character = Depends(get_character_for_user),
    db: Session = Depends(get_db),
):
    """Entfernt die Verknüpfung zwischen einem Charakter und einem Item."""
    association = character_repo.get_item_association(
        db, character_id=character.id, item_id=item_id
    )
    if not association:
        raise_api_error(
            404, "ITEM_NOT_FOUND", "Item nicht gefunden oder nicht mit Charakter verbunden."
        )

    character_repo.remove_item_from_character(db=db, association=association)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
