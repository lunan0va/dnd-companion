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


def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise_api_error(401, "INVALID_TOKEN", "Could not validate credentials")
        return username
    except JWTError:
        raise_api_error(401, "INVALID_TOKEN", "Could not validate credentials")

DbSession = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    username = decode_access_token(token)
    user = user_repo.get_by_username(db=db, username=username)
    if user is None:
        raise_api_error(401, "INVALID_TOKEN", "Could not validate credentials")
    return user

CurrentUser = Annotated[UserResponse, Depends(get_current_user)]


@router.get("/users", response_model=list[UserResponse], summary="Retrieve all users")
def get_users(db: Session = Depends(get_db)):
    # Verwende das Repository
    return user_repo.get_all(db=db)

@router.post("/register", response_model=Token, summary="Register a new user and get an access token")
def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = user_repo.get_by_username(db=db, username=user_data.username)
    if existing_user:
        raise_api_error(409, "USERNAME_ALREADY_EXISTS", "Username already exists")

    new_user = user_repo.create(db=db, user_in=user_data)

    access_token = create_access_token(data={"sub": new_user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/login", response_model=Token, summary="Authenticate user and get an access token")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = user_repo.get_by_username(db=db, username=form_data.username)
    if not user:
        raise_api_error(401, "INVALID_CREDENTIALS", "Invalid username or password")

    if not bcrypt.verify(form_data.password, user.password_hash):
        raise_api_error(401, "INVALID_CREDENTIALS", "Invalid username or password")

    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse, summary="Get current user information")
def read_users_me(current_user: UserResponse = Depends(get_current_user)):
    return current_user