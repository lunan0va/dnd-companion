"""
Definiert ein generisches Basis-Repository für CRUD-Operationen.

Dieses Modul stellt die `BaseRepository`-Klasse bereit, die eine wiederverwendbare
Schnittstelle für grundlegende Datenbankoperationen (Create, Read, Update, Delete)
bietet. Sie verwendet Python Generics und TypeVars, um stark typisiert und
flexibel für jedes SQLAlchemy-Modell zu sein.
"""
from typing import Generic, Type, TypeVar, List, Optional, Any
from pydantic import BaseModel
from sqlalchemy.orm import Session
from models import Base

ModelT = TypeVar("ModelT", bound=Base)
CreateSchemaT = TypeVar("CreateSchemaT", bound=BaseModel)
UpdateSchemaT = TypeVar("UpdateSchemaT", bound=BaseModel)


class BaseRepository(Generic[ModelT, CreateSchemaT, UpdateSchemaT]):
    """
    Eine generische Basisklasse für den Datenzugriff, die CRUD-Methoden implementiert.

    Args:
        model: Das SQLAlchemy-Modell, mit dem dieses Repository arbeitet
               (z.B. User, Character).
    """

    def __init__(self, model: Type[ModelT]):
        """
        Initialisiert das Repository mit einem spezifischen SQLAlchemy-Modell.
        """
        self.model = model

    def get(self, db: Session, obj_id: Any) -> Optional[ModelT]:
        """
        Ruft ein einzelnes Objekt anhand seiner ID aus der Datenbank ab.

        Args:
            db: Die aktive SQLAlchemy-Datenbanksession.
            obj_id: Die ID des zu suchenden Objekts.

        Returns:
            Das gefundene SQLAlchemy-Objekt oder None, wenn es nicht existiert.
        """
        return db.query(self.model).filter(self.model.id == obj_id).first()

    def get_all(self, db: Session) -> List[ModelT]:
        """
        Ruft alle Objekte eines bestimmten Typs aus der Datenbank ab.

        Args:
            db: Die aktive SQLAlchemy-Datenbanksession.

        Returns:
            Eine Liste aller gefundenen SQLAlchemy-Objekte.
        """
        return db.query(self.model).all()

    def create(self, db: Session, *, obj_in: CreateSchemaT) -> ModelT:
        """
        Erstellt ein neues Objekt in der Datenbank aus einem Pydantic-Schema.

        Args:
            db: Die aktive SQLAlchemy-Datenbanksession.
            obj_in: Das Pydantic-Schema mit den Daten für das neue Objekt.

        Returns:
            Das neu erstellte und in der Datenbank gespeicherte SQLAlchemy-Objekt.
        """
        obj_in_data = obj_in.model_dump()
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update(
        self, db: Session, *, db_obj: ModelT, obj_in: UpdateSchemaT
    ) -> ModelT:
        """
        Aktualisiert ein bestehendes Datenbank-Objekt mit Daten aus einem Pydantic-Schema.

        Args:
            db: Die aktive SQLAlchemy-Datenbanksession.
            db_obj: Das aus der DB geladene SQLAlchemy-Objekt, das aktualisiert werden soll.
            obj_in: Das Pydantic-Schema mit den neuen Daten.

        Returns:
            Das aktualisierte SQLAlchemy-Objekt.
        """
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def delete(self, db: Session, *, obj_id: int) -> Optional[ModelT]:
        """
        Löscht ein Objekt anhand seiner ID aus der Datenbank.

        Args:
            db: Die aktive SQLAlchemy-Datenbanksession.
            obj_id: Die ID des zu löschenden Objekts.

        Returns:
            Das gelöschte Objekt oder None, wenn es nicht gefunden wurde.
        """
        obj = db.query(self.model).get(obj_id)
        if obj:
            db.delete(obj)
            db.commit()
        return obj
