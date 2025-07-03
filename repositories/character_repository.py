from typing import List, Optional
from sqlalchemy.orm import Session, selectinload

from models.db_models import Character, CharacterSpell, CharacterItem, Spell, Item
from models.schemas import CharacterCreate, CharacterUpdate

class CharacterRepository:

    def get_by_id_and_user(self, db: Session, *, character_id: int, user_id: int) -> Optional[Character]:
        return db.query(Character).options(
            selectinload(Character.spells).joinedload(CharacterSpell.spell),
            selectinload(Character.items).joinedload(CharacterItem.item)
        ).filter(Character.id == character_id, Character.user_id == user_id).first()

    def get_all_for_user(self, db: Session, *, user_id: int) -> List[Character]:
        return db.query(Character).options(
            selectinload(Character.spells).joinedload(CharacterSpell.spell),
            selectinload(Character.items).joinedload(CharacterItem.item)
        ).filter(Character.user_id == user_id).all()

    def create_for_user(self, db: Session, *, obj_in: CharacterCreate, user_id: int) -> Character:
        new_character = Character(**obj_in.model_dump(), user_id=user_id)
        db.add(new_character)
        db.commit()
        db.refresh(new_character)
        return new_character

    def update(self, db: Session, *, db_obj: Character, obj_in: CharacterUpdate) -> Character:
        update_data = obj_in.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_obj, key, value)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, db_obj: Character) -> None:
        db.delete(db_obj)
        db.commit()

    def add_spell_to_character(self, db: Session, *, character: Character, spell_id: int) -> CharacterSpell:
        association = CharacterSpell(character_id=character.id, spell_id=spell_id)
        db.add(association)
        db.commit()
        db.refresh(association)
        return association

    def get_spell_association(self, db: Session, *, character_id: int, spell_id: int) -> Optional[CharacterSpell]:
        return db.query(CharacterSpell).filter_by(character_id=character_id, spell_id=spell_id).first()

    def remove_spell_from_character(self, db: Session, *, association: CharacterSpell):
        db.delete(association)
        db.commit()

    def add_item_to_character(self, db: Session, *, character: Character, item_id: int) -> CharacterItem:
        association = CharacterItem(character_id=character.id, item_id=item_id)
        db.add(association)
        db.commit()
        db.refresh(association)
        return association

    def get_item_association(self, db: Session, *, character_id: int, item_id: int) -> Optional[CharacterItem]:
        return db.query(CharacterItem).filter_by(character_id=character_id, item_id=item_id).first()

    def remove_item_from_character(self, db: Session, *, association: CharacterItem):
        db.delete(association)
        db.commit()

character_repo = CharacterRepository()