"""
Tests für die Character-Endpunkte, einschließlich CRUD und Verknüpfungen.
"""


def test_character_full_crud_flow(auth_client, mocker):
    """
    Testet den kompletten Lebenszyklus eines Charakters:
    Create -> Read (all) -> Read (one) -> Update -> Delete.
    """
    mocker.patch('routes.characters.fetch_dnd_classes_from_api', return_value=["Fighter", "Wizard"])

    create_response = auth_client.post(
        "/characters",
        json={"name": "Grog", "gameclass": "Fighter", "level": 5}
    )
    assert create_response.status_code == 201
    char_data = create_response.json()
    assert char_data["name"] == "Grog"
    character_id = char_data["id"]

    get_all_response = auth_client.get("/characters")
    assert get_all_response.status_code == 200
    assert len(get_all_response.json()) == 1
    assert get_all_response.json()[0]["id"] == character_id

    get_one_response = auth_client.get(f"/characters/{character_id}")
    assert get_one_response.status_code == 200
    assert get_one_response.json()["name"] == "Grog"

    update_response = auth_client.put(
        f"/characters/{character_id}",
        json={"name": "Grog Strongjaw", "level": 6}
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Grog Strongjaw"
    assert update_response.json()["level"] == 6

    delete_response = auth_client.delete(f"/characters/{character_id}")
    assert delete_response.status_code == 204

    verify_response = auth_client.get(f"/characters/{character_id}")
    assert verify_response.status_code == 404


def test_character_spell_association_flow(auth_client, mocker):
    """
    Testet das Hinzufügen und Entfernen eines Zaubers zu einem Charakter.
    """
    mocker.patch('routes.characters.fetch_dnd_classes_from_api', return_value=["Wizard"])
    mock_spell_data = {
        "index": "magic-missile", "name": "Magic Missile", "desc": ["..."],
        "level": 1, "casting_time": "1 Action", "range": "120 feet",
        "components": ["V", "S"], "duration": "Instantaneous", "school": {"name": "Evocation"}
    }
    mocker.patch('routes.helpers.fetch_details_from_dnd_api', return_value=mock_spell_data)
    mocker.patch('routes.helpers.translate_text_with_deepl', side_effect=lambda t, l: f"{t} ({l})")

    char_res = auth_client.post("/characters", json={"name": "Caleb", "gameclass": "Wizard"})
    character_id = char_res.json()["id"]
    spell_res = auth_client.post("/spells", json={"name": "magic missile"})
    spell_id = spell_res.json()["id"]

    add_res = auth_client.post(f"/characters/{character_id}/spells/{spell_id}")
    assert add_res.status_code == 201
    char_with_spell = add_res.json()
    assert len(char_with_spell["spells"]) == 1
    assert char_with_spell["spells"][0]["name_de"] == "Magic Missile (de)"

    duplicate_res = auth_client.post(f"/characters/{character_id}/spells/{spell_id}")
    assert duplicate_res.status_code == 409

    remove_res = auth_client.delete(f"/characters/{character_id}/spells/{spell_id}")
    assert remove_res.status_code == 204

    final_char_res = auth_client.get(f"/characters/{character_id}")
    assert len(final_char_res.json()["spells"]) == 0


def test_character_item_association_flow(auth_client, mocker):
    """
    Testet das Hinzufügen und Entfernen eines Items zu einem Charakter.
    """
    mocker.patch('routes.characters.fetch_dnd_classes_from_api', return_value=["Fighter"])
    mock_item_data = {
        "index": "greatsword", "name": "Greatsword", "desc": ["A mighty two-handed sword."]
    }
    mocker.patch('routes.helpers.fetch_details_from_dnd_api', return_value=mock_item_data)
    mocker.patch('routes.helpers.translate_text_with_deepl', side_effect=lambda t, l: f"{t} ({l})")

    char_res = auth_client.post("/characters", json={"name": "Grog", "gameclass": "Fighter"})
    character_id = char_res.json()["id"]
    item_res = auth_client.post("/items", json={"name": "greatsword"})
    item_id = item_res.json()["id"]

    add_res = auth_client.post(f"/characters/{character_id}/items/{item_id}")
    assert add_res.status_code == 201
    char_with_item = add_res.json()
    assert len(char_with_item["items"]) == 1
    assert char_with_item["items"][0]["name_de"] == "Greatsword (de)"

    duplicate_res = auth_client.post(f"/characters/{character_id}/items/{item_id}")
    assert duplicate_res.status_code == 409

    remove_res = auth_client.delete(f"/characters/{character_id}/items/{item_id}")
    assert remove_res.status_code == 204

    final_char_res = auth_client.get(f"/characters/{character_id}")
    assert len(final_char_res.json()["items"]) == 0


def test_create_character_with_invalid_class(auth_client, mocker):
    """Testet, dass die Charaktererstellung mit einer ungültigen Klasse fehlschlägt."""
    mocker.patch('routes.characters.fetch_dnd_classes_from_api', return_value=["Fighter", "Wizard"])

    create_response = auth_client.post(
        "/characters",
        json={"name": "Grog", "gameclass": "Barbarian", "level": 5}
    )
    assert create_response.status_code == 400
    assert create_response.json()["detail"]["error"]["code"] == "INVALID_CLASS_NAME"


def test_user_cannot_access_other_users_character(auth_client, client, mocker):
    """
    Stellt sicher, dass ein Benutzer eine 404-Fehlermeldung erhält,
    wenn er versucht, auf den Charakter eines anderen Benutzers zuzugreifen.
    """
    mocker.patch('routes.characters.fetch_dnd_classes_from_api', return_value=["Fighter"])

    create_response = auth_client.post(
        "/characters",
        json={"name": "Grog", "gameclass": "Fighter", "level": 5}
    )
    assert create_response.status_code == 201
    character_id = create_response.json()["id"]

    client.post("/register", json={"username": "user2", "password": "password2"})
    login_res = client.post("/login", data={"username": "user2", "password": "password2"})
    token2 = login_res.json()["access_token"]
    client.headers = {"Authorization": f"Bearer {token2}"}

    get_response = client.get(f"/characters/{character_id}")
    assert get_response.status_code == 404
    assert get_response.json()["detail"]["error"]["code"] == "CHARACTER_NOT_FOUND"
