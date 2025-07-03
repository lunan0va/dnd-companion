import os
import requests
from typing import List, Optional
from dotenv import load_dotenv
from .errors import raise_api_error

load_dotenv()

DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
DEEPL_API_URL = "https://api-free.deepl.com/v2/translate"

_DND_CLASSES_CACHE: Optional[List[str]] = None

def normalize_name(name: str) -> str:
    return name.lower().replace(" ", "-")

def fetch_details_from_dnd_api(endpoint: str, name_normalized: str) -> Optional[dict]:
    url = f"https://www.dnd5eapi.co/api/{endpoint}/{name_normalized}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None
        raise e
    except requests.exceptions.RequestException as e:
        raise_api_error(503, "SERVICE_UNAVAILABLE", f"Error fetching from D&D API: {e}")

def translate_text_with_deepl(text: str, target_lang: str) -> str:
    if not DEEPL_API_KEY or not text:
        return "Translation not available."
    try:
        params = {
            "auth_key": DEEPL_API_KEY,
            "text": text,
            "target_lang": target_lang.upper()
        }
        response = requests.post(DEEPL_API_URL, data=params)
        response.raise_for_status()
        translated_text = response.json()["translations"][0]["text"]
        return translated_text
    except requests.exceptions.RequestException as e:
        print(f"DeepL API Error: {e}")
        return "Translation failed."

def fetch_dnd_classes_from_api() -> List[str]:
    global _DND_CLASSES_CACHE
    if _DND_CLASSES_CACHE is not None:
        return _DND_CLASSES_CACHE

    url = "https://www.dnd5eapi.co/api/classes"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        classes = [item["name"] for item in data.get("results", [])]
        _DND_CLASSES_CACHE = classes
        return classes
    except Exception as e:
        raise_api_error(
            503,
            "SERVICE_UNAVAILABLE",
            f"Error fetching classes from D&D API: {e}"
        )