"""
Dieses Modul enthält das Repository für alle datenbankspezifischen Operationen,
die sich auf die Character-Entität beziehen.
"""
from typing import List, Optional

from sqlalchemy.orm import Session, selectinload

from models import Character, CharacterSpell, CharacterItem
from models.schemas import CharacterCreate, CharacterUpdate
from .base import BaseRepository


class CharacterRepository(BaseRepository[Character, CharacterCreate, CharacterUpdate]):
    """
    Repository für den Datenzugriff auf Character-Objekte.

    Erbt von der BaseRepository für generische CRUD-Funktionen und implementiert
    zusätzliche, charakter-spezifische Methoden.
    """

    def __init__(self):
        """Initialisiert das Repository mit dem Character-Modell."""
        super().__init__(model=Character)

    def get_by_id_and_user(
        self, db: Session, *, character_id: int, user_id: int
    ) -> Optional[Character]:
        """
        Ruft einen Charakter anhand seiner ID und der des Besitzers ab.

        Lädt dabei die verknüpften Spells und Items mittels Eager Loading,
        um die Anzahl der Datenbankabfragen zu minimieren (N+1 Problem).
        """
        return (
            db.query(Character)
            .options(
                selectinload(Character.spells).joinedload(CharacterSpell.spell),
                selectinload(Character.items).joinedload(CharacterItem.item),
            )
            .filter(Character.id == character_id, Character.user_id == user_id)
            .first()
        )

    def get_all_for_user(self, db: Session, *, user_id: int) -> List[Character]:
        """
        Ruft alle Charaktere für einen bestimmten Benutzer ab.

        Lädt dabei ebenfalls die verknüpften Spells und Items mittels Eager Loading.
        """
        return (
            db.query(Character)
            .options(
                selectinload(Character.spells).joinedload(CharacterSpell.spell),
                selectinload(Character.items).joinedload(CharacterItem.item),
            )
            .filter(Character.user_id == user_id)
            .all()
        )

    def create_for_user(
        self, db: Session, *, obj_in: CharacterCreate, user_id: int
    ) -> Character:
        """Erstellt einen neuen Charakter für einen bestimmten Benutzer."""
        new_character = Character(**obj_in.model_dump(), user_id=user_id)
        db.add(new_character)
        db.commit()
        db.refresh(new_character)
        return new_character

    def add_spell_to_character(
        self, db: Session, *, character: Character, spell_id: int
    ) -> CharacterSpell:
        """Fügt einem Charakter einen Zauber hinzu (erstellt die Verknüpfung)."""
        association = CharacterSpell(character_id=character.id, spell_id=spell_id)
        db.add(association)
        db.commit()
        db.refresh(association)
        return association

    def get_spell_association(
        self, db: Session, *, character_id: int, spell_id: int
    ) -> Optional[CharacterSpell]:
        """Prüft, ob ein Charakter einen bestimmten Zauber bereits besitzt."""
        return (
            db.query(CharacterSpell)
            .filter_by(character_id=character_id, spell_id=spell_id)
            .first()
        )

    def remove_spell_from_character(self, db: Session, *, association: CharacterSpell):
        """Entfernt die Verknüpfung eines Zaubers von einem Charakter."""
        db.delete(association)
        db.commit()

    def add_item_to_character(
        self, db: Session, *, character: Character, item_id: int
    ) -> CharacterItem:
        """Fügt einem Charakter ein Item hinzu (erstellt die Verknüpfung)."""
        association = CharacterItem(character_id=character.id, item_id=item_id)
        db.add(association)
        db.commit()
        db.refresh(association)
        return association

    def get_item_association(
        self, db: Session, *, character_id: int, item_id: int
    ) -> Optional[CharacterItem]:
        """Prüft, ob ein Charakter ein bestimmtes Item bereits besitzt."""
        return (
            db.query(CharacterItem)
            .filter_by(character_id=character_id, item_id=item_id)
            .first()
        )

    def remove_item_from_character(self, db: Session, *, association: CharacterItem):
        """Entfernt die Verknüpfung eines Items von einem Charakter."""
        db.delete(association)
        db.commit()


character_repo = CharacterRepository()
