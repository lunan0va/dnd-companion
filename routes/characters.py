from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from database import engine
from sqlalchemy import MetaData, select, insert, update, delete

router = APIRouter()

metadata = MetaData()
metadata.reflect(bind=engine)
characters = metadata.tables['characters']

class CharacterCreate(BaseModel):
    name: str
    gameclass: str
    level: int
    user_id: int

class CharacterUpdate(BaseModel):
    name: Optional[str] = None
    gameclass: Optional[str] = None
    level: Optional[int] = None
    user_id: Optional[int] = None

@router.get("/characters")
def get_characters():
    with engine.connect() as conn:
        result = conn.execute(select(characters)).fetchall()
        return [dict(row._mapping) for row in result]


@router.get("/characters/{character_id}")
def get_character(character_id: int):
    with engine.connect() as conn:
        stmt = select(characters).where(characters.c.id == character_id)
        result = conn.execute(stmt).first()
        if not result:
            raise HTTPException(status_code=404, detail="Character not found")
        row = result._mapping
        return {
            "id": row["id"],
            "name": row["name"],
            "gameclass": row["gameclass"],
            "level": row["level"],
            "user_id": row["user_id"]
        }

@router.post("/characters")
def create_character(char: CharacterCreate):
    with engine.connect() as conn:
        stmt = insert(characters).values(
            name=char.name,
            gameclass=char.gameclass,
            level=char.level,
            user_id=char.user_id
        )
        result = conn.execute(stmt)
        conn.commit()
        return {
            "id": result.inserted_primary_key[0],
            "name": char.name,
            "gameclass": char.gameclass,
            "level": char.level,
            "user_id": char.user_id
        }

@router.put("/characters/{character_id}")
def update_character(character_id: int, char: CharacterUpdate):
    update_data = {}
    if char.name is not None:
        update_data["name"] = char.name
    if char.gameclass is not None:
        update_data["gameclass"] = char.gameclass
    if char.level is not None:
        update_data["level"] = char.level
    if char.user_id is not None:
        update_data["user_id"] = char.user_id
    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    with engine.connect() as conn:
        stmt = (
            update(characters)
            .where(characters.c.id == character_id)
            .values(**update_data)
        )
        result = conn.execute(stmt)
        conn.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Character not found")
        return {"message": "Character updated"}

@router.delete("/characters/{character_id}")
def delete_character(character_id: int):
    with engine.connect() as conn:
        stmt = delete(characters).where(characters.c.id == character_id)
        result = conn.execute(stmt)
        conn.commit()
        if result.rowcount == 0:
            raise HTTPException(status_code=404, detail="Character not found")
        return {"message": "Character deleted"}
