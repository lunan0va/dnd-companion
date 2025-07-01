import os
import re
from datetime import datetime
from typing import List, Optional

import requests
import deepl
from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from dotenv import load_dotenv

from database import get_db
from models import Item
from routes.users import get_current_user, UserResponse

router = APIRouter()

load_dotenv()
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
if not DEEPL_API_KEY:
    raise ValueError("DEEPL_API_KEY environment variable not set.")


def _normalize_item_name(name: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def fetch_item_details_from_dnd_api(item_index: str):
    url = f"https://www.dnd5eapi.co/api/equipment/{item_index}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=f"Error fetching from D&D API: {e}")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                            detail=f"Network error connecting to D&D API: {e}")


def translate_text_with_deepl(text_en: str, target_lang: str = 'de') -> str:
    try:
        translator = deepl.Translator(DEEPL_API_KEY)
        result = translator.translate_text(text_en, target_lang=target_lang)
        return result.text
    except deepl.exceptions.DeepLException as e:
        return f"DeepL API Error: {e}"
    except Exception as e:
        return f"ERROR: {e}"


class ItemCreateRequest(BaseModel):
    name: str

# TODO: DB etc. anpassen, da Waffen z.B. keine Beschreibung haben
class ItemResponse(BaseModel):
    id: int
    dnd_api_id: str
    name_en: str
    name_de: str
    description_en: Optional[str] = None
    description_de: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/items", response_model=List[ItemResponse], summary="Retrieve all items")
def get_all_items(db: Session = Depends(get_db)):
    items_from_db = db.query(Item).all()
    if not items_from_db:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No items found.")
    return items_from_db


@router.get("/items/{item_id}", response_model=ItemResponse, summary="Retrieve a single item by ID")
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found.")
    return item


@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED,
             summary="Create a new item from D&D API by name")
def create_item_from_api(request: ItemCreateRequest, current_user: UserResponse = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    item_name_en_normalized = _normalize_item_name(request.name)

    existing_item = db.query(Item).filter(Item.dnd_api_id == item_name_en_normalized).first()
    if existing_item:
        return existing_item

    api_data = fetch_item_details_from_dnd_api(item_name_en_normalized)

    if not api_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Item '{request.name}' not found on D&D 5e API.")

    name_en = api_data.get("name")
    description_en = "\n".join(api_data.get("desc", []))

    name_de = translate_text_with_deepl(name_en, 'de')
    description_de = translate_text_with_deepl(description_en, 'de')

    new_item = Item(
        dnd_api_id=api_data.get("index"),
        name_en=name_en,
        name_de=name_de,
        description_en=description_en,
        description_de=description_de,
    )
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return new_item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an item")
def delete_item(item_id: int, current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found.")

    db.delete(item)
    db.commit()
    return
