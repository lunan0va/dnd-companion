from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from utils.errors import raise_api_error
from utils.dnd_api_client import normalize_name, fetch_details_from_dnd_api, translate_text_with_deepl

from models.schemas import ItemCreateRequest, ItemResponse
from models.db_models import Item

from repositories import item_repo

from .users import get_current_user, UserResponse

router = APIRouter()


@router.get("/items", response_model=List[ItemResponse], summary="Retrieve all items")
def get_all_items(db: Session = Depends(get_db)):
    return item_repo.get_all(db=db)


@router.get("/items/{item_id}", response_model=ItemResponse, summary="Retrieve a single item by ID")
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = item_repo.get(db=db, id=item_id)
    if not item:
        raise_api_error(404, "ITEM_NOT_FOUND", "Item not found.")
    return item


@router.post("/items", response_model=ItemResponse, status_code=status.HTTP_201_CREATED,
             summary="Create a new item from D&D API by name")
def create_item_from_api(request: ItemCreateRequest, current_user: UserResponse = Depends(get_current_user),
                         db: Session = Depends(get_db)):
    item_name_en_normalized = normalize_name(request.name)

    existing_item = item_repo.get_by_dnd_api_id(db=db, dnd_api_id=item_name_en_normalized)
    if existing_item:
        return existing_item

    api_data = fetch_details_from_dnd_api("equipment", item_name_en_normalized)
    if not api_data:
        raise_api_error(404, "ITEM_NOT_FOUND", "Item not found on D&D 5e API.")

    name_en = api_data.get("name")
    description_en = "\n".join(api_data.get("desc", []))

    name_de = translate_text_with_deepl(name_en, 'de')
    description_de = translate_text_with_deepl(description_en, 'de')

    new_item_model = Item(
        dnd_api_id=api_data.get("index"),
        name_en=name_en,
        name_de=name_de,
        description_en=description_en,
        description_de=description_de,
    )

    return item_repo.create_from_model(db=db, db_obj=new_item_model)


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete an item")
def delete_item(item_id: int, current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    deleted_item = item_repo.delete(db=db, id=item_id)
    if not deleted_item:
        raise_api_error(404, "ITEM_NOT_FOUND", "Item not found.")
    return
