"""
Ein Client-Modul für die Interaktion mit externen APIs.

Stellt Funktionen zur Verfügung, um Daten von der D&D 5e API abzurufen
und Texte mit der DeepL API zu übersetzen. Enthält auch Caching für
wiederholte Anfragen.
"""
import os
from functools import lru_cache
from typing import List, Optional

import httpx
from dotenv import load_dotenv

from .errors import raise_api_error

load_dotenv()

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"
REQUEST_TIMEOUT = 10


def normalize_name(name: str) -> str:
    """
    Normalisiert einen Namen für die Verwendung in einer URL.

    Wandelt den String in Kleinbuchstaben um und ersetzt Leerzeichen durch Bindestriche.
    """
    return name.lower().replace(" ", "-")


# pylint: disable=inconsistent-return-statements
async def fetch_details_from_dnd_api(endpoint: str, name_normalized: str) -> Optional[dict]:
    """
    Ruft Detailinformationen von einem bestimmten Endpunkt der D&D 5e API ab.

    Args:
        endpoint: Der API-Endpunkt (z.B. 'spells', 'equipment').
        name_normalized: Der normalisierte Name des gesuchten Objekts.

    Returns:
        Ein Dictionary mit den API-Daten oder None, wenn das Objekt nicht gefunden wurde (404).
        Löst bei anderen Fehlern eine Exception aus.
    """
    url = f"https://www.dnd5eapi.co/api/2014/{endpoint}/{name_normalized}"
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise e
    except httpx.RequestError as e:
        raise_api_error(503, "SERVICE_UNAVAILABLE", f"Error fetching from D&D API: {e}")


async def translate_text_with_deepl(text: str, target_lang: str) -> str:
    """
    Übersetzt einen gegebenen Text mit der DeepL API.

    Gibt einen Platzhaltertext zurück, wenn kein API-Schlüssel konfiguriert ist
    oder ein Fehler auftritt.
    """
    if not DEEPL_API_KEY or not text:
        return "Übersetzung nicht verfügbar."
    try:
        params = {
            "auth_key": DEEPL_API_KEY,
            "text": text,
            "target_lang": target_lang.upper(),
        }
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.post(DEEPL_API_URL, data=params)
            response.raise_for_status()
            translated_text = response.json()["translations"][0]["text"]
            return translated_text
    except httpx.RequestError as e:
        raise_api_error(503, "TRANSLATION_FAILED", f"DeepL API Error: {e}")


@lru_cache(maxsize=1)
# pylint: disable=inconsistent-return-statements
async def fetch_dnd_classes_from_api() -> List[str]:
    """
    Ruft die Liste der verfügbaren Charakterklassen von der D&D 5e API ab.

    Das Ergebnis wird zwischengespeichert (gecached), um wiederholte API-Aufrufe
    zu vermeiden.
    """
    url = "https://www.dnd5eapi.co/api/2014/classes"
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            response = await client.get(url, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            data = response.json()
            return [item["name"] for item in data.get("results", [])]
    except httpx.RequestError as e:
        raise_api_error(
            503, "SERVICE_UNAVAILABLE", f"Error fetching classes from D&D API: {e}"
        )
