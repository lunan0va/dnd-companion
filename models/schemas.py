# pylint: disable=too-few-public-methods
"""
Definiert die Pydantic-Schemas für die API-Datenvalidierung und Serialisierung.

Dieses Modul enthält alle Modelle, die für die Ein- und Ausgabe von API-Endpunkten
verwendet werden. Sie stellen sicher, dass die an die API gesendeten Daten korrekt
strukturiert sind und definieren das Format der JSON-Antworten.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, field_validator, ConfigDict

from .db_models import CharacterSpell, CharacterItem


# Schemas für User & Authentication

class UserCreate(BaseModel):
    """Schema für die Erstellung eines neuen Benutzers."""
    username: str
    password: str


class UserResponse(BaseModel):
    """Schema für die Antwort bei Benutzer-Abfragen (ohne Passwort)."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    created_at: datetime


class Token(BaseModel):
    """Schema für den JWT Access Token."""
    access_token: str
    token_type: str


# Schemas für Items

class ItemCreateRequest(BaseModel):
    """Schema für die Anfrage zur Erstellung eines Items über die D&D API."""
    name: str


class ItemResponse(BaseModel):
    """Schema für die vollständige Antwort eines Items."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    dnd_api_id: str
    name_en: str
    name_de: str
    description_en: Optional[str] = None
    description_de: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# Schemas für Spells

class SpellCreateRequest(BaseModel):
    """Schema für die Anfrage zur Erstellung eines Zaubers über die D&D API."""
    name: str


class SpellResponse(BaseModel):
    """Schema für die vollständige Antwort eines Zaubers."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    dnd_api_id: str
    name_en: str
    name_de: str
    description_en: Optional[str] = None
    description_de: Optional[str] = None
    level: Optional[int] = None
    casting_time: Optional[str] = None
    spell_range: Optional[str] = None
    components: Optional[str] = None
    duration: Optional[str] = None
    school: Optional[str] = None
    created_at: datetime
    updated_at: datetime


# Schemas für Characters

class CharacterCreate(BaseModel):
    """Schema für die Erstellung eines neuen Charakters."""
    name: str
    gameclass: str
    level: int = 1


class CharacterUpdate(BaseModel):
    """Schema für die Aktualisierung eines Charakters. Alle Felder sind optional."""
    name: Optional[str] = None
    gameclass: Optional[str] = None
    level: Optional[int] = None


class SpellForCharacterResponse(BaseModel):
    """Ein abgespecktes Zauber-Schema, nur für die Anzeige in einer Charakter-Antwort."""
    model_config = ConfigDict(from_attributes=True)

    name_de: str
    description_de: Optional[str] = None
    level: Optional[int] = None
    casting_time: Optional[str] = None
    spell_range: Optional[str] = None
    components: Optional[str] = None
    duration: Optional[str] = None


class ItemForCharacterResponse(BaseModel):
    """Ein abgespecktes Item-Schema, nur für die Anzeige in einer Charakter-Antwort."""
    model_config = ConfigDict(from_attributes=True)

    name_de: str
    description_de: Optional[str] = None


class CharacterResponse(BaseModel):
    """Das vollständige Antwort-Schema für einen Charakter, inkl. seiner Items und Spells."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    gameclass: str
    level: int
    user_id: int
    created_at: datetime
    updated_at: datetime
    spells: List[SpellForCharacterResponse] = []
    items: List[ItemForCharacterResponse] = []

    @field_validator('spells', mode='before')
    @classmethod
    def transform_spells(cls, v):
        """
        Transformiert die Assoziationsobjekte (CharacterSpell) in Spell-Objekte.
        """
        if isinstance(v, list) and all(isinstance(i, CharacterSpell) for i in v):
            return [cs.spell for cs in v]
        return v

    @field_validator('items', mode='before')
    @classmethod
    def transform_items(cls, v):
        """
        Transformiert die Assoziationsobjekte (CharacterItem) in Item-Objekte.
        """
        if isinstance(v, list) and all(isinstance(i, CharacterItem) for i in v):
            return [ci.item for ci in v]
        return v
