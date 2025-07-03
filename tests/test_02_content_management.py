"""
Tests für die Spells und Items Endpunkte.

Diese Tests verwenden Mocks, um externe API-Aufrufe zu simulieren,
damit die Tests schnell und unabhängig von externen Diensten sind.
"""

# Spell Tests

def test_spell_flow(auth_client, mocker):
    """Testet den Flow für das Erstellen, Abrufen und Löschen eines Zaubers."""
    mock_dnd_api_data = {
        "index": "fire-bolt",
        "name": "Fire Bolt",
        "desc": ["You hurl a mote of fire at a creature or object within range."],
        "level": 0,
        "casting_time": "1 Action",
        "range": "120 feet",
        "components": ["V", "S"],
        "duration": "Instantaneous",
        "school": {"name": "Evocation"}
    }
    mocker.patch(
        'routes.helpers.fetch_details_from_dnd_api',
        return_value=mock_dnd_api_data
    )
    mocker.patch(
        'routes.helpers.translate_text_with_deepl',
        side_effect=lambda text, lang: f"{text} ({lang})"
    )

    create_response = auth_client.post("/spells", json={"name": "fire bolt"})
    assert create_response.status_code == 201
    spell_data = create_response.json()
    assert spell_data["name_en"] == "Fire Bolt"
    assert spell_data["name_de"] == "Fire Bolt (de)"
    assert spell_data["level"] == 0
    spell_id = spell_data["id"]

    get_response = auth_client.get(f"/spells/{spell_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name_en"] == "Fire Bolt"

    delete_response = auth_client.delete(f"/spells/{spell_id}")
    assert delete_response.status_code == 204

    verify_response = auth_client.get(f"/spells/{spell_id}")
    assert verify_response.status_code == 404


# Item Tests

def test_item_flow(auth_client, mocker):
    """Testet den Flow für das Erstellen, Abrufen und Löschen eines Items."""
    mock_dnd_api_data = {
        "index": "longsword",
        "name": "Longsword",
        "desc": ["A versatile martial weapon."]
    }
    mocker.patch(
        'routes.helpers.fetch_details_from_dnd_api',
        return_value=mock_dnd_api_data
    )
    mocker.patch(
        'routes.helpers.translate_text_with_deepl',
        side_effect=lambda text, lang: f"{text} ({lang})"
    )

    create_response = auth_client.post("/items", json={"name": "longsword"})
    assert create_response.status_code == 201
    item_data = create_response.json()
    assert item_data["name_en"] == "Longsword"
    assert item_data["name_de"] == "Longsword (de)"
    item_id = item_data["id"]

    get_response = auth_client.get(f"/items/{item_id}")
    assert get_response.status_code == 200
    assert get_response.json()["name_en"] == "Longsword"

    delete_response = auth_client.delete(f"/items/{item_id}")
    assert delete_response.status_code == 204

    verify_response = auth_client.get(f"/items/{item_id}")
    assert verify_response.status_code == 404
