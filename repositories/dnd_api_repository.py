"""
Definiert eine spezialisierte Basis-Repository für Objekte, die von der D&D API stammen.
"""
from typing import Optional, TypeVar
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import Base
from .base import BaseRepository

ModelT = TypeVar("ModelT", bound=Base)
CreateSchemaT = TypeVar("CreateSchemaT", bound=BaseModel)
UpdateSchemaT = TypeVar("UpdateSchemaT", bound=BaseModel)


class DndApiObjectRepository(BaseRepository[ModelT, CreateSchemaT, UpdateSchemaT]):
    """
    Eine Basis-Repository für Modelle, die von der D&D 5e API zwischengespeichert werden.

    Stellt gemeinsame Methoden zur Verfügung, um Objekte anhand ihrer dnd_api_id
    abzurufen und um manuell erstellte Objekte zu speichern.
    """

    def get_by_dnd_api_id(self, db: Session, *, dnd_api_id: str) -> Optional[ModelT]:
        """Sucht ein Objekt in der lokalen Datenbank anhand seiner D&D-API-ID."""
        # Geht davon aus, dass das Modell ein 'dnd_api_id'-Attribut hat.
        return db.query(self.model).filter(self.model.dnd_api_id == dnd_api_id).first()

    def save(self, db: Session, *, db_obj: ModelT) -> ModelT:
        """
        Speichert ein bereits erstelltes SQLAlchemy-Modellobjekt in der Datenbank.

        Wird verwendet, wenn das Objekt manuell (z.B. nach einer API-Anfrage)
        erstellt wurde und nun persistiert werden soll.
        """
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj
