"""
Dieses Modul enthält das Repository für alle datenbankspezifischen Operationen,
die sich auf die User-Entität beziehen, einschließlich der Passwort-Verwaltung.
"""
from typing import Optional

from pydantic import BaseModel
from sqlalchemy.orm import Session
from passlib.hash import bcrypt

from models import User
from models.schemas import UserCreate
from .base import BaseRepository


class UserRepository(BaseRepository[User, UserCreate, BaseModel]):
    """
    Repository für den Datenzugriff auf User-Objekte.

    Erbt von der BaseRepository und überschreibt die `create`-Methode,
    um die sichere Speicherung von Passwörtern durch Hashing zu gewährleisten.
    """

    def __init__(self):
        """Initialisiert das Repository mit dem User-Modell."""
        super().__init__(model=User)

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        """
        Sucht einen Benutzer in der Datenbank anhand seines eindeutigen Benutzernamens.

        Args:
            db: Die aktive SQLAlchemy-Datenbanksession.
            username: Der zu suchende Benutzername.

        Returns:
            Das gefundene User-Objekt oder None, wenn es nicht existiert.
        """
        return db.query(User).filter(User.username == username).first()

    def create(self, db: Session, *, obj_in: UserCreate) -> User:
        """
        Erstellt einen neuen Benutzer und hasht sein Passwort vor dem Speichern.

        Überschreibt die generische `create`-Methode der BaseRepository.

        Args:
            db: Die aktive SQLAlchemy-Datenbanksession.
            obj_in: Das Pydantic-Schema mit den Daten des neuen Benutzers.

        Returns:
            Das neu erstellte und in der Datenbank gespeicherte User-Objekt.
        """
        hashed_password = bcrypt.hash(obj_in.password)
        # Erstelle das DB-Objekt manuell, um das Passwort-Feld korrekt zu setzen
        db_obj = User(username=obj_in.username, password_hash=hashed_password)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj


user_repo = UserRepository()
