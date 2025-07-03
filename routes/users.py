"""
Definiert die API-Endpunkte für die Benutzer-Authentifizierung und -Verwaltung.

Dieses Modul enthält die Routen für die Registrierung neuer Benutzer,
das Einloggen (Erstellen von JWTs) und das Abrufen von Benutzerinformationen.
"""
import os
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from jose import JWTError, jwt
from dotenv import load_dotenv

from database import get_db
from utils.errors import raise_api_error
from models.schemas import UserCreate, Token, UserResponse
from repositories import user_repo

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

router = APIRouter()


def create_access_token(data: dict) -> str:
    """
    Erstellt einen neuen JWT Access Token.

    Args:
        data: Ein Dictionary mit den Daten, die in den Token kodiert werden sollen.

    Returns:
        Der kodierte JWT als String.
    """
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# pylint: disable=inconsistent-return-statements
def decode_access_token(token: str) -> str:
    """
    Dekodiert einen JWT Access Token und validiert ihn.

    Args:
        token: Der zu dekodierende JWT-String.

    Raises:
        HTTPException: Wenn der Token ungültig, abgelaufen oder manipuliert ist.

    Returns:
        Der Benutzername (sub) aus dem Token-Payload.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            # KORREKTUR: Fehlermeldung auf Deutsch
            raise_api_error(
                401, "INVALID_TOKEN", "Anmeldeinformationen konnten nicht validiert werden."
            )
        return username
    except JWTError:
        # KORREKTUR: Fehlermeldung auf Deutsch
        raise_api_error(
            401, "INVALID_TOKEN", "Anmeldeinformationen konnten nicht validiert werden."
        )


DbSession = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]


def get_current_user(token: TokenDep, db: DbSession) -> UserResponse:
    """
    Dependency, die den aktuellen Benutzer anhand des JWT-Tokens aus der DB abruft.

    Wird verwendet, um Endpunkte zu schützen und den eingeloggten Benutzer zu identifizieren.

    Raises:
        HTTPException: Wenn der Token ungültig ist oder der Benutzer nicht existiert.

    Returns:
        Das Pydantic-Schema des aktuellen Benutzers.
    """
    username = decode_access_token(token)
    user = user_repo.get_by_username(db=db, username=username)
    if user is None:
        # KORREKTUR: Fehlermeldung auf Deutsch
        raise_api_error(
            401, "INVALID_TOKEN", "Anmeldeinformationen konnten nicht validiert werden."
        )
    return user


CurrentUser = Annotated[UserResponse, Depends(get_current_user)]


@router.post(
    "/register",
    response_model=Token,
    summary="Einen neuen Benutzer registrieren und einen Access Token erhalten",
)
def register_user(user_data: UserCreate, db: DbSession):
    """
    Registriert einen neuen Benutzer in der Datenbank.

    Prüft, ob der Benutzername bereits existiert. Wenn nicht, wird der Benutzer
    erstellt und ein neuer Access Token für die sofortige Anmeldung zurückgegeben.
    """
    existing_user = user_repo.get_by_username(db=db, username=user_data.username)
    if existing_user:
        # KORREKTUR: Fehlermeldung auf Deutsch
        raise_api_error(409, "USERNAME_ALREADY_EXISTS", "Benutzername existiert bereits.")

    new_user = user_repo.create(db=db, obj_in=user_data)

    access_token = create_access_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login",
             response_model=Token,
             summary="Benutzer authentifizieren und Access Token erhalten")
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: DbSession):
    """
    Authentifiziert einen Benutzer anhand von Benutzername und Passwort.

    Bei erfolgreicher Authentifizierung wird ein neuer JWT Access Token zurückgegeben.
    """
    user = user_repo.get_by_username(db=db, username=form_data.username)
    if not user or not bcrypt.verify(form_data.password, user.password_hash):
        # KORREKTUR: Fehlermeldung auf Deutsch
        raise_api_error(401, "INVALID_CREDENTIALS", "Ungültiger Benutzername oder Passwort.")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Informationen zum aktuellen Benutzer abrufen")
def read_users_me(current_user: CurrentUser):
    """Gibt die Informationen des aktuell eingeloggten Benutzers zurück."""
    return current_user
