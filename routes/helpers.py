"""
Hilfsfunktionen für die API-Routen, um Code-Duplizierung zu vermeiden.
"""
from typing import Type, Callable, Optional
from pydantic import BaseModel, ConfigDict
from sqlalchemy.orm import Session
from models import Base
from repositories.dnd_api_repository import DndApiObjectRepository
from utils.dnd_api_client import (
    normalize_name,
    fetch_details_from_dnd_api,
    translate_text_with_deepl,
)
from utils.errors import raise_api_error


# pylint: disable=too-few-public-methods
class APIObjectConfig(BaseModel):
    """
    Konfiguration für das Abrufen/Erstellen eines API-Objekts.

    Bündelt alle notwendigen Parameter, um die `get_or_create_api_object`-Funktion
    sauber und erweiterbar zu halten.
    """

    repo: DndApiObjectRepository
    model_class: Type[Base]
    api_endpoint: str
    extra_fields_factory: Optional[Callable[[dict], dict]] = None

    model_config = ConfigDict(arbitrary_types_allowed=True)


def get_or_create_api_object(
    db: Session,
    request_name: str,
    config: APIObjectConfig,
) -> Base:
    """
    Holt ein Objekt aus der DB oder erstellt es via D&D-API, wenn es nicht existiert.

    Kapselt die Logik des Nachsehens, Abrufens, Übersetzens, Erstellens und Speicherns.
    """
    normalized_name = normalize_name(request_name)

    existing_obj = config.repo.get_by_dnd_api_id(db=db, dnd_api_id=normalized_name)
    if existing_obj:
        return existing_obj

    api_data = fetch_details_from_dnd_api(config.api_endpoint, normalized_name)
    if not api_data:
        raise_api_error(
            404,
            f"{config.model_class.__name__.upper()}_NOT_FOUND",
            f"{config.model_class.__name__} nicht in der D&D 5e API gefunden.",
        )

    name_en = api_data.get("name")
    description_en = "\n".join(api_data.get("desc", []))
    name_de = translate_text_with_deepl(name_en, "de")
    description_de = translate_text_with_deepl(description_en, "de")

    model_data = {
        "dnd_api_id": api_data.get("index"),
        "name_en": name_en,
        "name_de": name_de,
        "description_en": description_en,
        "description_de": description_de,
    }
    if config.extra_fields_factory:
        model_data.update(config.extra_fields_factory(api_data))

    new_db_obj = config.model_class(**model_data)
    return config.repo.save(db=db, db_obj=new_db_obj)
