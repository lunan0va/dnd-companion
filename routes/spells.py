from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from utils.errors import raise_api_error
from utils.dnd_api_client import normalize_name, fetch_details_from_dnd_api, translate_text_with_deepl

from models.schemas import SpellCreateRequest, SpellResponse
from models.db_models import Spell

from repositories import spell_repo

from .users import get_current_user, UserResponse

router = APIRouter()


@router.get("/spells", response_model=List[SpellResponse], summary="Retrieve all spells")
def get_all_spells(db: Session = Depends(get_db)):
    # Die Logik ist jetzt sauber im Repository gekapselt.
    return spell_repo.get_all(db=db)


@router.get("/spells/{spell_id}", response_model=SpellResponse, summary="Retrieve a single spell by ID")
def get_spell(spell_id: int, db: Session = Depends(get_db)):
    # Viel sauberer und klarer als der direkte DB-Aufruf.
    spell = spell_repo.get(db=db, id=spell_id)
    if not spell:
        raise_api_error(404, "SPELL_NOT_FOUND", "Spell not found.")
    return spell


@router.post("/spells", response_model=SpellResponse, status_code=status.HTTP_201_CREATED,
             summary="Create a new spell from D&D API by name")
def create_spell_from_api(request: SpellCreateRequest, current_user: UserResponse = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    spell_name_en_normalized = normalize_name(request.name)

    existing_spell = spell_repo.get_by_dnd_api_id(db=db, dnd_api_id=spell_name_en_normalized)
    if existing_spell:
        return existing_spell

    api_data = fetch_details_from_dnd_api("spells", spell_name_en_normalized)
    if not api_data:
        raise_api_error(404, "SPELL_NOT_FOUND", "Spell not found on D&D 5e API.")

    name_en = api_data.get("name")
    description_en = "\n".join(api_data.get("desc", []))

    name_de = translate_text_with_deepl(name_en, 'de')
    description_de = translate_text_with_deepl(description_en, 'de')

    new_spell_model = Spell(
        dnd_api_id=api_data.get("index"),
        name_en=name_en,
        name_de=name_de,
        description_en=description_en,
        description_de=description_de,
        level=api_data.get("level"),
        casting_time=api_data.get("casting_time"),
        range=api_data.get("range"),
        components=", ".join(api_data.get("components", [])),
        duration=api_data.get("duration"),
        school=api_data.get("school", {}).get("name")
    )

    return spell_repo.create_from_model(db=db, db_obj=new_spell_model)


@router.delete("/spells/{spell_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a spell")
def delete_spell(spell_id: int, current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    deleted_spell = spell_repo.delete(db=db, id=spell_id)
    if not deleted_spell:
        raise_api_error(404, "SPELL_NOT_FOUND", "Spell not found.")
    return