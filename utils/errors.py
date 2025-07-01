from fastapi import HTTPException, status


def raise_api_error(status_code: int, code: str, message: str):
    raise HTTPException(
        status_code=status_code,
        detail={"error": {"code": code, "message": message}}
    )