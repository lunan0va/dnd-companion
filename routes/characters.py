from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from database import get_db
from utils.errors import raise_api_error
from utils.dnd_api_client import fetch_dnd_classes_from_api

from models.schemas import CharacterCreate, CharacterUpdate, CharacterResponse

from repositories import character_repo, spell_repo, item_repo

from .users import get_current_user, UserResponse

router = APIRouter()


@router.get("/characters", response_model=List[CharacterResponse],
            summary="Retrieve all characters for the current user")
def get_all_characters(current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    return character_repo.get_all_for_user(db=db, user_id=current_user.id)


@router.get("/characters/{character_id}", response_model=CharacterResponse, summary="Retrieve a single character by ID")
def get_character(character_id: int, current_user: UserResponse = Depends(get_current_user),
                  db: Session = Depends(get_db)):
    character = character_repo.get_by_id_and_user(db=db, character_id=character_id, user_id=current_user.id)
    if not character:
        raise_api_error(404, "CHARACTER_NOT_FOUND", "Character not found or not owned by user.")
    return character


@router.post("/characters", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED,
             summary="Create a new character")
def create_character(char_create: CharacterCreate, current_user: UserResponse = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    valid_classes = fetch_dnd_classes_from_api()
    if char_create.gameclass.lower() not in [cls.lower() for cls in valid_classes]:
        raise_api_error(400, "INVALID_CLASS_NAME",
                        "Invalid class name. Allowed classes are: " + ", ".join(valid_classes))

    return character_repo.create_for_user(db=db, obj_in=char_create, user_id=current_user.id)


@router.put("/characters/{character_id}", response_model=CharacterResponse, summary="Update an existing character")
def update_character(character_id: int, char_update: CharacterUpdate,
                     current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    character = character_repo.get_by_id_and_user(db=db, character_id=character_id, user_id=current_user.id)
    if not character:
        raise_api_error(404, "CHARACTER_NOT_FOUND", "Character not found or not owned by user.")

    update_data = char_update.model_dump(exclude_unset=True)
    if "gameclass" in update_data:
        valid_classes = fetch_dnd_classes_from_api()
        if update_data["gameclass"].lower() not in [cls.lower() for cls in valid_classes]:
            raise_api_error(400, "INVALID_CLASS_NAME", "Invalid class name.")

    return character_repo.update(db=db, db_obj=character, obj_in=char_update)


@router.delete("/characters/{character_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a character")
def delete_character(character_id: int, current_user: UserResponse = Depends(get_current_user),
                     db: Session = Depends(get_db)):
    character = character_repo.get_by_id_and_user(db=db, character_id=character_id, user_id=current_user.id)
    if not character:
        raise_api_error(404, "CHARACTER_NOT_FOUND", "Character not found or not owned by user.")

    character_repo.delete(db=db, db_obj=character)
    return


@router.post("/characters/{character_id}/spells/{spell_id}", status_code=status.HTTP_201_CREATED,
             summary="Add a spell to a character")
def add_spell_to_character(character_id: int, spell_id: int, current_user: UserResponse = Depends(get_current_user),
                           db: Session = Depends(get_db)):
    character = character_repo.get_by_id_and_user(db=db, character_id=character_id, user_id=current_user.id)
    if not character:
        raise_api_error(404, "CHARACTER_NOT_FOUND", "Character not found or not owned by user.")

    spell = spell_repo.get(db, id=spell_id)
    if not spell:
        raise_api_error(404, "SPELL_NOT_FOUND", "Spell not found.")

    if character_repo.get_spell_association(db, character_id=character_id, spell_id=spell_id):
        raise_api_error(409, "SPELL_ALREADY_ASSOCIATED", "Spell is already associated with this character.")

    character_repo.add_spell_to_character(db=db, character=character, spell_id=spell_id)
    return {"message": f"Spell '{spell.name_en}' added to character '{character.name}' successfully."}


@router.delete("/characters/{character_id}/spells/{spell_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Remove a spell from a character")
def remove_spell_from_character(character_id: int, spell_id: int,
                                current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    character = character_repo.get_by_id_and_user(db=db, character_id=character_id, user_id=current_user.id)
    if not character:
        raise_api_error(404, "CHARACTER_NOT_FOUND", "Character not found or not owned by user.")

    association = character_repo.get_spell_association(db, character_id=character_id, spell_id=spell_id)
    if not association:
        raise_api_error(404, "SPELL_NOT_FOUND", "Spell not found or not associated with this character.")

    character_repo.remove_spell_from_character(db=db, association=association)
    return


@router.post("/characters/{character_id}/items/{item_id}", status_code=status.HTTP_201_CREATED,
             summary="Add an item to a character")
def add_item_to_character(character_id: int, item_id: int, current_user: UserResponse = Depends(get_current_user),
                          db: Session = Depends(get_db)):
    character = character_repo.get_by_id_and_user(db=db, character_id=character_id, user_id=current_user.id)
    if not character:
        raise_api_error(404, "CHARACTER_NOT_FOUND", "Character not found or not owned by user.")

    item = item_repo.get(db, id=item_id)
    if not item:
        raise_api_error(404, "ITEM_NOT_FOUND", "Item not found.")

    if character_repo.get_item_association(db, character_id=character_id, item_id=item_id):
        raise_api_error(409, "ITEM_ALREADY_ASSOCIATED", "Item is already associated with this character.")

    character_repo.add_item_to_character(db=db, character=character, item_id=item_id)
    return {"message": f"Item '{item.name_en}' added to character '{character.name}' successfully."}


@router.delete("/characters/{character_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT,
               summary="Remove an item from a character")
def remove_item_from_character(character_id: int, item_id: int,
                               current_user: UserResponse = Depends(get_current_user), db: Session = Depends(get_db)):
    character = character_repo.get_by_id_and_user(db=db, character_id=character_id, user_id=current_user.id)
    if not character:
        raise_api_error(404, "CHARACTER_NOT_FOUND", "Character not found or not owned by user.")

    association = character_repo.get_item_association(db, character_id=character_id, item_id=item_id)
    if not association:
        raise_api_error(404, "ITEM_NOT_FOUND", "Item not found or not associated with this character.")

    character_repo.remove_item_from_character(db=db, association=association)
    return