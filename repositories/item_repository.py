from typing import Optional
from sqlalchemy.orm import Session
from models.db_models import Item
from .base import BaseRepository

class ItemRepository(BaseRepository[Item]):
    def get_by_dnd_api_id(self, db: Session, *, dnd_api_id: str) -> Optional[Item]:
        return db.query(self.model).filter(self.model.dnd_api_id == dnd_api_id).first()

    def create_from_model(self, db: Session, *, db_obj: Item) -> Item:
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

item_repo = ItemRepository(Item)