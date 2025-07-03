# pylint: disable=too-few-public-methods
"""
Definiert die SQLAlchemy ORM-Modelle für die D&D Companion-Anwendung.

Dieses Modul enthält das Datenbankschema für alle primären Entitäten,
einschließlich Benutzer, Charaktere, Items und Zauber, sowie die
Assoziationstabellen für deren Many-to-Many-Beziehungen.
"""
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """Repräsentiert einen authentifizierten Benutzer der Anwendung."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now)
    updated_at = Column(DateTime(timezone=True), server_default=func.now, onupdate=func.now)

    characters = relationship("Character", back_populates="owner")


class Character(Base):
    """Repräsentiert einen von einem Spieler erstellten Charakter."""
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    gameclass = Column(String)
    level = Column(Integer, default=1)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now)
    updated_at = Column(DateTime(timezone=True), server_default=func.now, onupdate=func.now)

    owner = relationship("User", back_populates="characters")
    items = relationship(
        "CharacterItem", back_populates="character", cascade="all, delete-orphan"
    )
    spells = relationship(
        "CharacterSpell", back_populates="character", cascade="all, delete-orphan"
    )


class Item(Base):
    """
    Repräsentiert ein generisches Item, das aus der externen D&D-API
    zwischengespeichert wird.
    """
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    dnd_api_id = Column(String, unique=True, nullable=False)
    name_en = Column(String, nullable=False)
    name_de = Column(String, nullable=False)
    description_en = Column(Text)
    description_de = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now)
    updated_at = Column(DateTime(timezone=True), server_default=func.now, onupdate=func.now)

    character_items = relationship("CharacterItem", back_populates="item")


class Spell(Base):
    """
    Repräsentiert einen generischen Zauber, der aus der externen D&D-API
    zwischengespeichert wird.
    """
    __tablename__ = "spells"

    id = Column(Integer, primary_key=True, index=True)
    dnd_api_id = Column(String, unique=True, nullable=False)
    name_en = Column(String, nullable=False)
    name_de = Column(String, nullable=False)
    description_en = Column(Text)
    description_de = Column(Text)
    level = Column(Integer)
    casting_time = Column(String)
    spell_range = Column("range", String)
    components = Column(String)
    duration = Column(String)
    school = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now)
    updated_at = Column(DateTime(timezone=True), server_default=func.now, onupdate=func.now)

    character_spells = relationship("CharacterSpell", back_populates="spell")


class CharacterItem(Base):
    """Assoziationstabelle, die Charaktere mit ihren Items verbindet."""
    __tablename__ = "character_items"

    character_id = Column(Integer, ForeignKey("characters.id"), primary_key=True)
    item_id = Column(Integer, ForeignKey("items.id"), primary_key=True)

    character = relationship("Character", back_populates="items")
    item = relationship("Item", back_populates="character_items")


class CharacterSpell(Base):
    """Assoziationstabelle, die Charaktere mit ihren Zaubern verbindet."""
    __tablename__ = "character_spells"

    character_id = Column(Integer, ForeignKey("characters.id"), primary_key=True)
    spell_id = Column(Integer, ForeignKey("spells.id"), primary_key=True)

    character = relationship("Character", back_populates="spells")
    spell = relationship("Spell", back_populates="character_spells")

    __table_args__ = (UniqueConstraint("character_id", "spell_id", name="_character_spell_uc"),)
