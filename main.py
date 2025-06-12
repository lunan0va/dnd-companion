from fastapi import FastAPI
from routes import users, characters

app = FastAPI()

app.include_router(users.router)
app.include_router(characters.router)

