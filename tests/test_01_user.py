"""
End-to-End-Tests für den Benutzer-Authentifizierungs-Flow.

Testet die API-Endpunkte für die Registrierung und das Einloggen von Benutzern.
"""


def test_register_and_login_flow(client):
    """
    Testet den kompletten User-Flow: Registrierung und anschließendes Einloggen.
    Der 'client'-Parameter wird uns automatisch von pytest aus der conftest.py gegeben.
    """
    response = client.post(
        "/register",
        json={"username": "test_user", "password": "a_secure_password"}
    )

    assert response.status_code == 201
    token_data = response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"

    login_response = client.post(
        "/login",
        data={"username": "test_user", "password": "a_secure_password"}
    )

    assert login_response.status_code == 200
    assert "access_token" in login_response.json()

    failed_login_response = client.post(
        "/login",
        data={"username": "test_user", "password": "wrong_password"}
    )

    assert failed_login_response.status_code == 401
