"""
Ein Hilfsmodul zur standardisierten Behandlung von API-Fehlern.
"""
from fastapi import HTTPException


def raise_api_error(status_code: int, code: str, message: str):
    """
    Löst eine standardisierte HTTPException mit einem benutzerdefinierten Detail-Payload aus.

    Dies stellt sicher, dass alle API-Fehler im gesamten Projekt eine konsistente
    JSON-Struktur haben.

    Args:
        status_code: Der HTTP-Statuscode (z.B. 404, 409).
        code: Ein anwendungsspezifischer Fehlercode (z.B. "USER_NOT_FOUND").
        message: Eine für den Benutzer lesbare Fehlermeldung.

    Raises:
        HTTPException: Eine FastAPI HTTPException, die die API-Antwort generiert.
    """
    raise HTTPException(
        status_code=status_code,
        detail={"error": {"code": code, "message": message}},
    )
