import pytest
from meetdown.meetdown import MeetDown

@pytest.fixture
def meetdown():
    config = MeetDown.default_config()
    return MeetDown(config)

def test_preview_returns_list_of_strings(meetdown):
    md_data = {
        "Entity 1": {
            "Category 1": [
                {"external_ticket": "FD-123", "description": "Description 1"}
            ]
        }
    }
    result = meetdown.preview(md_data)
    assert isinstance(result, list)
    assert all(isinstance(item, str) for item in result)

def test_choices_of_add_method(meetdown):
    expected_choices = "1. Add\n2. Remove\n3. Toggle\n4. Load\n5. Save & Quit"
    result = meetdown.generate_options()
    print(expected_choices)
    assert result == expected_choices

def test_toggle_status_moves_item_to_new_category(meetdown):
    # Set up initial data
    md_data = {
        "Entity 1": {
            "Category 1": [
                {"external_ticket": "FD-123", "description": "Description 1"}
            ],
            "Category 2": []
        }
    }
    meetdown.md_data = md_data

    # Toggle the item from "Category 1" to "Category 2"
    meetdown.toggle_status("Entity 1", "Category 1", "Category 2", {"external_ticket": "FD-123", "description": "Description 1"})

    # Verify that the item has been moved to "Category 2"
    assert meetdown.md_data["Entity 1"]["Category 1"] == []
    assert meetdown.md_data["Entity 1"]["Category 2"] == [{"external_ticket": "FD-123", "description": "Description 1"}]

def test_toggle_status_creates_new_category_if_not_exists(meetdown):
    # Set up initial data with no "Category 2"
    md_data = {
        "Entity 1": {
            "Category 1": [
                {"external_ticket": "FD-123", "description": "Description 1"}
            ]
        }
    }
    meetdown.md_data = md_data

    # Toggle the item from "Category 1" to "Category 2"
    meetdown.toggle_status("Entity 1", "Category 1", "Category 2", {"external_ticket": "FD-123", "description": "Description 1"})

    # Verify that "Category 2" has been created and the item has been moved to it
    assert "Category 2" in meetdown.md_data["Entity 1"]
    assert meetdown.md_data["Entity 1"]["Category 1"] == []
    assert meetdown.md_data["Entity 1"]["Category 2"] == [{"external_ticket": "FD-123", "description": "Description 1"}]

def test_toggle_status_does_nothing_if_item_not_found(meetdown):
    # Set up initial data
    md_data = {
        "Entity 1": {
            "Category 1": [
                {"external_ticket": "FD-123", "description": "Description 1"}
            ],
            "Category 2": []
        }
    }
    meetdown.md_data = md_data

    # Toggle an item that does not exist
    meetdown.toggle_status("Entity 1", "Category 2", "Category 1", {"external_ticket": "FD-456", "description": "Description 2"})

    # Verify that the data remains unchanged
    assert meetdown.md_data == md_data

def test_add_item(meetdown):
    # Set up initial data
    meetdown.md_data = {
        "Entity 1": {
            "Category 1": [],
            "Category 2": []
        }
    }

    # Add a new item to "Category 1"
    meetdown.add_item("Entity 1", "Category 1", "FD-123", "Description 1")

    # Verify that the item has been added to "Category 1"
    assert len(meetdown.md_data["Entity 1"]["Category 1"]) == 1
    assert meetdown.md_data["Entity 1"]["Category 1"][0]["external_ticket"] == "FD-123"
    assert meetdown.md_data["Entity 1"]["Category 1"][0]["description"] == "Description 1"

def test_add_entity(meetdown):
    # Set up initial data
    meetdown.md_data = {}

    # Add a new entity
    meetdown.add_entity("Entity 1")

    # Verify that the entity has been added with all categories from the config
    assert "Entity 1" in meetdown.md_data
    assert meetdown.md_data["Entity 1"] == {
        "⬜": [],
        "✅": []
    }

def test_remove_item(meetdown):
    # Set up initial data
    meetdown.md_data = {
        "Entity 1": {
            "Category 1": [
                {"external_ticket": "FD-123", "description": "Description 1"},
                {"external_ticket": "FD-456", "description": "Description 2"}
            ],
            "Category 2": []
        }
    }

    # Remove the first item from "Category 1"
    meetdown.remove_item("Entity 1", "Category 1", 0)

    # Verify that the item has been removed from "Category 1"
    assert len(meetdown.md_data["Entity 1"]["Category 1"]) == 1
    assert meetdown.md_data["Entity 1"]["Category 1"][0]["external_ticket"] == "FD-456"
    assert meetdown.md_data["Entity 1"]["Category 1"][0]["description"] == "Description 2"

def test_remove_entity(meetdown):
    # Set up initial data
    meetdown.md_data = {
        "Entity 1": {
            "Category 1": [],
            "Category 2": []
        },
        "Entity 2": {
            "Category 1": [],
            "Category 2": []
        }
    }

    # Remove "Entity 1"
    meetdown.remove_entity("Entity 1")

    # Verify that "Entity 1" has been removed
    assert "Entity 1" not in meetdown.md_data

def test_ensure_default_ctx_items_exist_in_md_data(meetdown):
    # Set up initial data with missing ctx items
    meetdown.md_data = {
        "Entity 1": {
            "⬜": []
        },
        "Entity 2": {
            "⬜": [],
            "✅": []
        }
    }

    # Ensure default ctx items exist
    meetdown.ensure_default_ctx_items_exist_in_md_data()

    # Verify that missing ctx items have been added
    assert "✅" in meetdown.md_data["Entity 1"]
    assert meetdown.md_data["Entity 1"]["✅"]