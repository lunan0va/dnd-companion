"""
Macht das 'models'-Verzeichnis zu einem Python-Paket und exportiert die wichtigsten Klassen.

Dies ermöglicht sauberere Importe aus anderen Modulen. Man kann zum Beispiel
`from models import User` verwenden, anstatt des längeren `from models.db_models import User`.
"""
from .db_models import (
    Base,
    User,
    Character,
    Item,
    Spell,
    CharacterSpell,
    CharacterItem,
)
