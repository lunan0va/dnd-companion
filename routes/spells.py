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
from models import Spell
from routes.users import get_current_user, UserResponse

router = APIRouter()

load_dotenv()
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
if not DEEPL_API_KEY:
    raise ValueError("DEEPL_API_KEY environment variable not set.")


def _normalize_spell_name(name: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def fetch_spell_details_from_dnd_api(spell_index: str):
    url = "https://www.dnd5eapi.co/api/spells/{spell_index}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail=f"Error fetching from D&D API: {e}")
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE,detail=f"Network error connecting to D&D API: {e}")


def translate_text_with_deepl(text_en: str, target_lang: str = 'de') -> str:
    try:
        translator = deepl.Translator(DEEPL_API_KEY)
        result = translator.translate_text(text_en, target_lang=target_lang)
        return result.text
    except deepl.exceptions.DeepLException as e:
        return f"DeepL API Error: {e}"
    except Exception as e:
        return f"ERROR: {e}"


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
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No spells found.")
    return spells_from_db


@router.get("/spells/{spell_id}", response_model=SpellResponse, summary="Retrieve a single spell by ID")
def get_spell(spell_id: int, db: Session = Depends(get_db)):
    spell = db.query(Spell).filter(Spell.id == spell_id).first()
    if not spell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spell not found.")
    return spell


@router.post("/spells", response_model=SpellResponse, status_code=status.HTTP_201_CREATED, summary="Create a new spell from D&D API by name")
def create_spell_from_api(request: SpellCreateRequest, current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    spell_name_en_normalized = _normalize_spell_name(request.name)

    existing_spell = db.query(Spell).filter(Spell.dnd_api_id == spell_name_en_normalized).first()
    if existing_spell:
        return existing_spell

    api_data = fetch_spell_details_from_dnd_api(spell_name_en_normalized)

    if not api_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Spell '{request.name}' not found on D&D 5e API.")

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
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spell not found.")

    db.delete(spell)
    db.commit()
    return