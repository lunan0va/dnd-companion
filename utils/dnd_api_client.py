import os
import re

import requests
import deepl
from dotenv import load_dotenv

from utils.errors import raise_api_error

load_dotenv()
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")
if not DEEPL_API_KEY:
    raise ValueError("DEEPL_API_KEY environment variable not set.")

def normalize_name(name: str) -> str:
    return re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')


def fetch_details_from_dnd_api(endpoint: str, item_index: str):
    url = f"https://www.dnd5eapi.co/api/{endpoint}/{item_index}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return None
        raise_api_error(
            503,
            "SERVICE_UNAVAILABLE",
            f"Error fetching from D&D API: {e}"
        )
    except requests.exceptions.RequestException as e:
        raise_api_error(
            503,
            "SERVICE_UNAVAILABLE",
            f"Network error connecting to D&D API: {e}"
        )


def translate_text_with_deepl(text_en: str, target_lang: str = 'de') -> str:
    if not text_en:
        return ""
    try:
        translator = deepl.Translator(DEEPL_API_KEY)
        result = translator.translate_text(text_en, target_lang=target_lang)
        return result.text
    except deepl.exceptions.DeepLException as e:
        raise_api_error(
            503,
            "SERVICE_UNAVAILABLE",
            f"DeepL translation service failed: {e}"
        )
    except Exception as e:
        raise_api_error(
            500,
            "INTERNAL_SERVER_ERROR",
            f"An unexpected error occurred during translation: {e}"
        )