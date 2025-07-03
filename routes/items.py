"""
Definiert die API-Endpunkte für die Verwaltung von Items.

Dieses Modul enthält Endpunkte zum Abrufen aller zwischengespeicherten Items,
zum Erstellen neuer Items durch Abfrage der externen D&D-API und zum Löschen.
"""
from typing import List

from fastapi import APIRouter, Depends, status, Response
from sqlalchemy.orm import Session

from database import get_db
from models import Item
from models.schemas import ItemCreateRequest, ItemResponse, UserResponse
from repositories import item_repo
from utils.errors import raise_api_error
from .users import get_current_user
from .helpers import get_or_create_api_object, APIObjectConfig

router = APIRouter()


@router.get("/items", response_model=List[ItemResponse], summary="Alle Items abrufen")
def get_all_items(db: Session = Depends(get_db)):
    """Ruft eine Liste aller Items ab, die im System zwischengespeichert sind."""
    return item_repo.get_all(db=db)


@router.get(
    "/items/{item_id}",
    response_model=ItemResponse,
    summary="Ein einzelnes Item anhand der ID abrufen",
)
def get_item(item_id: int, db: Session = Depends(get_db)):
    """Ruft ein einzelnes, zwischengespeichertes Item anhand seiner primären ID ab."""
    item = item_repo.get(db=db, obj_id=item_id)
    if not item:
        raise_api_error(404, "ITEM_NOT_FOUND", "Item nicht gefunden.")
    return item


@router.post(
    "/items",
    response_model=ItemResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Neues Item aus der D&D-API erstellen und zwischenspeichern",
)
def create_item_from_api(
    request: ItemCreateRequest,
    _current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Erstellt ein neues Item, indem es von der D&D 5e API abgerufen wird.
    Die Logik ist in eine wiederverwendbare Hilfsfunktion ausgelagert.
    """
    config = APIObjectConfig(
        repo=item_repo,
        model_class=Item,
        api_endpoint="equipment",
    )
    return get_or_create_api_object(
        db=db,
        request_name=request.name,
        config=config,
    )


@router.delete(
    "/items/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Ein Item löschen",
)
def delete_item(
    item_id: int,
    _current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Löscht ein zwischengespeichertes Item aus der Datenbank."""
    deleted_item = item_repo.delete(db=db, obj_id=item_id)
    if not deleted_item:
        raise_api_error(404, "ITEM_NOT_FOUND", "Item nicht gefunden.")

    return Response(status_code=status.HTTP_204_NO_CONTENT)
