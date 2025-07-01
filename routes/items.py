from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session


from database import get_db
from models import Item
from routes.users import get_current_user, UserResponse
from utils.dnd_api_client import normalize_name, fetch_details_from_dnd_api, translate_text_with_deepl

router = APIRouter()


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
    item_name_en_normalized = normalize_name(request.name)

    existing_item = db.query(Item).filter(Item.dnd_api_id == item_name_en_normalized).first()
    if existing_item:
        return existing_item

    api_data = fetch_details_from_dnd_api("equiment", item_name_en_normalized)

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
