from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Spell
from routes.users import get_current_user, UserResponse
from utils.dnd_api_client import normalize_name, fetch_details_from_dnd_api, translate_text_with_deepl
from utils.errors import raise_api_error


router = APIRouter()


class SpellCreateRequest(BaseModel):
    name: str


class SpellResponse(BaseModel):
    id: int
    dnd_api_id: str
    name_en: str
    name_de: str
    description_en: Optional[str] = None
    description_de: Optional[str] = None
    level: Optional[int] = None
    casting_time: Optional[str] = None
    range: Optional[str] = None
    components: Optional[str] = None
    duration: Optional[str] = None
    school: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.get("/spells", response_model=List[SpellResponse], summary="Retrieve all spells")
def get_all_spells(db: Session = Depends(get_db)):
    spells_from_db = db.query(Spell).all()
    if not spells_from_db:
        raise_api_error(
            404,
            "NO_SPELLS_FOUND",
            "No spells found."
        )
    return spells_from_db


@router.get("/spells/{spell_id}", response_model=SpellResponse, summary="Retrieve a single spell by ID")
def get_spell(spell_id: int, db: Session = Depends(get_db)):
    spell = db.query(Spell).filter(Spell.id == spell_id).first()
    if not spell:
        raise_api_error(
            404,
            "SPELL_NOT_FOUND",
            "Spell not found."
        )
    return spell


@router.post("/spells", response_model=SpellResponse, status_code=status.HTTP_201_CREATED,
             summary="Create a new spell from D&D API by name")
def create_spell_from_api(request: SpellCreateRequest, current_user: UserResponse = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    spell_name_en_normalized = normalize_name(request.name)

    existing_spell = db.query(Spell).filter(Spell.dnd_api_id == spell_name_en_normalized).first()
    if existing_spell:
        return existing_spell

    api_data = fetch_details_from_dnd_api("spells", spell_name_en_normalized)

    if not api_data:
        raise_api_error(
            404,
            "SPELL_NOT_FOUND",
            "Spell not found on D&D 5e API."
        )

    name_en = api_data.get("name")
    description_en = "\n".join(api_data.get("desc", []))

    name_de = translate_text_with_deepl(name_en, 'de')
    description_de = translate_text_with_deepl(description_en, 'de')

    higher_level_desc_en = "\n".join(api_data.get("higher_level", []))
    if higher_level_desc_en:
        description_en += "\n\nHigher Levels:\n" + higher_level_desc_en
        description_de += "\n\nHöhere Grade:\n" + translate_text_with_deepl(higher_level_desc_en, 'de')

    new_spell = Spell(
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
        school=api_data.get("school", {}).get("name"),
    )
    db.add(new_spell)
    db.commit()
    db.refresh(new_spell)

    return new_spell


@router.delete("/spells/{spell_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a spell")
def delete_spell(spell_id: int, current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    spell = db.query(Spell).filter(Spell.id == spell_id).first()
    if not spell:
        raise_api_error(
            404,
            "SPELL_NOT_FOUND",
            "Spell not found."
        )

    db.delete(spell)
    db.commit()
    return
