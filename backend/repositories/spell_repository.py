"""
Dieses Modul enthält das Repository für alle datenbankspezifischen Operationen,
die sich auf die Spell-Entität beziehen.
"""
from pydantic import BaseModel

from models import Spell
from models.schemas import SpellCreateRequest
# KORREKTUR: Von der neuen, spezialisierten Basisklasse erben
from .dnd_api_repository import DndApiObjectRepository


class SpellRepository(DndApiObjectRepository[Spell, SpellCreateRequest, BaseModel]):
    """
    Repository für den Datenzugriff auf Spell-Objekte.

    Erbt von DndApiObjectRepository, um die Logik für API-basierte Objekte
    wiederzuverwenden.
    """

    def __init__(self):
        """Initialisiert das Repository mit dem Spell-Modell."""
        super().__init__(model=Spell)


spell_repo = SpellRepository()
