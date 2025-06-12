from fastapi import APIRouter
from database import engine
from sqlalchemy import MetaData, select

router = APIRouter()

metadata = MetaData()
metadata.reflect(bind=engine)
users = metadata.tables['users']

@router.get("/users")
def get_users():
    with engine.connect() as conn:
        result = conn.execute(select(users.c.id, users.c.username)).fetchall()
        return [{"id": row.id, "username": row.username} for row in result]
