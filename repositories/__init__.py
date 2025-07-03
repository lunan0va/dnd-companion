"""
Macht das 'repositories'-Verzeichnis zu einem Python-Paket und exportiert
die Singleton-Instanzen der einzelnen Repositories.

Dies ermöglicht saubere und konsistente Importe in den API-Routen, z.B.:
`from repositories import user_repo`
"""
from .user_repository import user_repo
from .character_repository import character_repo
from .item_repository import item_repo
from .spell_repository import spell_repo
