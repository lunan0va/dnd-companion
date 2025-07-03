from typing import List, Optional
from sqlalchemy.orm import Session
from passlib.hash import bcrypt

from models.db_models import User
from models.schemas import UserCreate

class UserRepository:

    def get_by_username(self, db: Session, *, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    def get_all(self, db: Session) -> List[User]:
        return db.query(User).all()

    def create(self, db: Session, *, user_in: UserCreate) -> User:
        hashed_password = bcrypt.hash(user_in.password)
        db_obj = User(username=user_in.username, password_hash=hashed_password)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

user_repo = UserRepository()