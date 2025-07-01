from datetime import datetime
from typing import List, Optional

import requests
from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session, selectinload
from pydantic import BaseModel

from database import get_db
from models import Character, User, Spell, CharacterSpell, Item, CharacterItem
from routes.users import get_current_user, UserResponse

router = APIRouter()

_DND_CLASSES_CACHE: Optional[List[str]] = None


def fetch_dnd_classes_from_api() -> List[str]:
    global _DND_CLASSES_CACHE

    if _DND_CLASSES_CACHE is not None:
        return _DND_CLASSES_CACHE

    url = "https://www.dnd5eapi.co/api/classes"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        classes = [item["name"] for item in data.get("results", [])]

        _DND_CLASSES_CACHE = classes
        return classes
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching classes from D&D API: {e}"
        )


class CharacterCreate(BaseModel):
    name: str
    gameclass: str
    level: int = 1


class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    gameclass: Optional[str] = None
    level: Optional[int] = None


class SpellForCharacterResponse(BaseModel):
    name_de: str
    description_de: Optional[str] = None
    level: Optional[int] = None
    casting_time: Optional[str] = None
    range: Optional[str] = None
    components: Optional[str] = None
    duration: Optional[str] = None

    class Config:
        from_attributes = True


class ItemForCharacterResponse(BaseModel):
    name_de: str
    description_de: Optional[str] = None

    class Config:
        from_attributes = True


class CharacterResponse(BaseModel):
    id: int
    name: str
    gameclass: str
    level: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    spells: List[SpellForCharacterResponse] = []
    items: List[ItemForCharacterResponse] = []

    class Config:
        from_attributes = True


@router.get("/characters", response_model=List[CharacterResponse],
            summary="Retrieve all characters for the current user")
def get_all_characters(current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    characters = db.query(Character).options(
        selectinload(Character.character_spells).joinedload(CharacterSpell.spell)).filter(
        Character.user_id == current_user.id).all()

    if not characters:
        raise HTTPException(status_code=status.HTTP_204_NO_CONTENT, detail="No characters found for this user.")

    response_characters = []
    for char_orm in characters:
        char_dict = char_orm.__dict__.copy()

        char_dict["spells"] = [SpellForCharacterResponse.model_validate(cs.spell) for cs in char_orm.character_spells]
        char_dict["items"] = [ItemForCharacterResponse.model_validate(ci.item) for ci in char_orm.character_items]

        for k in list(char_dict.keys()):
            if k.startswith("_sa_"):
                del char_dict[k]

        response_characters.append(CharacterResponse(**char_dict))

    return response_characters


@router.get("/characters/{character_id}", response_model=CharacterResponse, summary="Retrieve a single character by ID")
def get_character(character_id: int, current_user: UserResponse = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    character = db.query(Character).options(
        selectinload(Character.character_spells).joinedload(CharacterSpell.spell)).filter(
        (Character.id == character_id) & (Character.user_id == current_user.id)).first()

    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found or not owned by user.")

    char_dict = character.__dict__.copy()
    char_dict["spells"] = [SpellForCharacterResponse.model_validate(cs.spell) for cs in character.character_spells]
    char_dict["items"] = [ItemForCharacterResponse.model_validate(ci.item) for ci in char_orm.character_items]

    for k in list(char_dict.keys()):
        if k.startswith("_sa_"):
            del char_dict[k]

    return CharacterResponse(**char_dict)


@router.post("/characters", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED,
             summary="Create a new character"
             )
def create_character(char_create: CharacterCreate, current_user: UserResponse = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    valid_classes = fetch_dnd_classes_from_api()

    if char_create.gameclass.lower() not in [cls.lower() for cls in valid_classes]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail=f"Invalid class name. Allowed classes are: {', '.join(valid_classes)}")

    new_character = Character(name=char_create.name, gameclass=char_create.gameclass, level=char_create.level,
                              user_id=current_user.id)
    db.add(new_character)
    db.commit()
    db.refresh(new_character)

    return new_character


@router.put("/characters/{character_id}", response_model=CharacterResponse, summary="Update an existing character")
def update_character(character_id: int, char_update: CharacterUpdate,
                     current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    character = db.query(Character).filter(
        (Character.id == character_id) & (Character.user_id == current_user.id)).first()

    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found or not owned by user")

    update_data = char_update.model_dump(exclude_unset=True)

    if "gameclass" in update_data:
        valid_classes = fetch_dnd_classes_from_api()
        if update_data["gameclass"].lower() not in [cls.lower() for cls in valid_classes]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"Invalid class name. Allowed classes are: {', '.join(valid_classes)}")

    for key, value in update_data.items():
        setattr(character, key, value)

    db.add(character)
    db.commit()
    db.refresh(character)

    return character


@router.delete("/characters/{character_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a character")
def delete_character(character_id: int, current_user: UserResponse = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    character = db.query(Character).filter(
        (Character.id == character_id) & (Character.user_id == current_user.id)).first()

    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found or not owned by user")

    db.delete(character)
    db.commit()

    return


@router.post("/characters/{character_id}/spells/{spell_id}", status_code=status.HTTP_201_CREATED,
             summary="Add a spell to a character")
def add_spell_to_character(character_id: int, spell_id: int, current_user: UserResponse = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    character = db.query(Character).filter(
        (Character.id == character_id) & (Character.user_id == current_user.id)).first()
    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found or not owned by user.")

    spell = db.query(Spell).filter(Spell.id == spell_id).first()
    if not spell:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Spell not found.")

    existing_association = db.query(CharacterSpell).filter(
        (CharacterSpell.character_id == character_id) & (CharacterSpell.spell_id == spell_id)).first()
    if existing_association:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Spell is already associated with this character.")

    character_spell = CharacterSpell(character_id=character_id, spell_id=spell_id)
    db.add(character_spell)
    db.commit()
    db.refresh(character_spell)

    return {"message": f"Spell '{spell.name_en}' added to character '{character.name}' successfully."}


@router.delete("/characters/{character_id}/spells/{spell_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Remove a spell from a character")
def remove_spell_from_character(character_id: int, spell_id: int,
                                current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    character = db.query(Character).filter(
        (Character.id == character_id) & (Character.user_id == current_user.id)
    ).first()
    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found or not owned by user.")

    association_to_delete = db.query(CharacterSpell).filter(
        (CharacterSpell.character_id == character_id) & (CharacterSpell.spell_id == spell_id)
    ).first()

    if not association_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Spell is not associated with this character.")

    db.delete(association_to_delete)
    db.commit()

    return


@router.post("/characters/{character_id}/items/{item_id}", status_code=status.HTTP_201_CREATED,
             summary="Add an item to a character")
def add_item_to_character(character_id: int, item_id: int, current_user: UserResponse = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    character = db.query(Character).filter(
        (Character.id == character_id) & (Character.user_id == current_user.id)).first()
    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found or not owned by user.")

    item = db.query(Item).filter(Item.id == item_id).first()
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found.")

    existing_association = db.query(CharacterItem).filter(
        (CharacterItem.character_id == character_id) & (CharacterItem.item_id == item_id)).first()
    if existing_association:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT,
                            detail="Item is already associated with this character.")

    character_item = CharacterItem(character_id=character_id, item_id=item_id)
    db.add(character_item)
    db.commit()

    return {"message": f"Item '{item.name_en}' added to character '{character.name}' successfully."}


@router.delete("/characters/{character_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Remove an item from a character")
def remove_item_from_character(character_id: int, item_id: int,
                               current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    character = db.query(Character).filter(
        (Character.id == character_id) & (Character.user_id == current_user.id)
    ).first()
    if not character:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Character not found or not owned by user.")

    association_to_delete = db.query(CharacterItem).filter(
        (CharacterItem.character_id == character_id) & (CharacterItem.item_id == item_id)
    ).first()

    if not association_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Item is not associated with this character.")

    db.delete(association_to_delete)
    db.commit()

    return
