"""
Dieses Modul enthält das Repository für alle datenbankspezifischen Operationen,
die sich auf die Item-Entität beziehen.
"""
from pydantic import BaseModel

from models import Item
from models.schemas import ItemCreateRequest
from .dnd_api_repository import DndApiObjectRepository


class ItemRepository(DndApiObjectRepository[Item, ItemCreateRequest, BaseModel]):
    """
    Repository für den Datenzugriff auf Item-Objekte.

    Erbt von DndApiObjectRepository, um die Logik für API-basierte Objekte
    wiederzuverwenden.
    """

    def __init__(self):
        """Initialisiert das Repository mit dem Item-Modell."""
        super().__init__(model=Item)


item_repo = ItemRepository()
