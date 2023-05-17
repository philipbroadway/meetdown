import pytest

from meetdown import MeetDown

@pytest.fixture
def meetdown():
    config = MeetDown.default_config()
    return MeetDown(config)


@pytest.fixture
def single_entity_single_item_with_external():
    return {
        "Entity 1": {
            "Category 1": [
                {"external_ticket": "FD-123", "description": "Description 1"}
            ]
        }
    }

@pytest.fixture
def category(root, category="Category 1"):
    root[category] = []
    return root

def test_preview_returns_list_of_strings(meetdown):
    d = single_entity_single_item_with_external()
    result = meetdown.preview(d)
    assert isinstance(result, list)
    assert all(isinstance(item, str) for item in result)

def test_choices_of_add_method(meetdown):
    expected_choices = "1. Add\n2. Edit\n3. Load\n4. Topggle\n5. Remove\n6. Quit & Save"
    result = meetdown.generate_options()
    print(expected_choices)
    assert result == expected_choices

def test_toggle_status_moves_item_to_new_category(meetdown):
    # Set up initial data
    data = {
        "Entity 1": {
            "Category 1": [
                {"external_ticket": "FD-123", "description": "Description 1"}
            ],
            "Category 2": []
        }
    }
    meetdown.data = data

    # Toggle the item from "Category 1" to "Category 2"
    meetdown.toggle_status("Entity 1", "Category 1", "Category 2", {"external_ticket": "FD-123", "description": "Description 1"})

    # Verify that the item has been moved to "Category 2"
    assert meetdown.data["Entity 1"]["Category 1"] == []
    assert meetdown.data["Entity 1"]["Category 2"] == [{"external_ticket": "FD-123", "description": "Description 1"}]

def test_toggle_status_creates_new_category_if_not_exists(meetdown):
    # Set up initial data with no "Category 2"
    data = {
        "Entity 1": {
            "Category 1": [
                {"external_ticket": "FD-123", "description": "Description 1"}
            ]
        }
    }
    meetdown.data = data

    # Toggle the item from "Category 1" to "Category 2"
    meetdown.toggle_status("Entity 1", "Category 1", "Category 2", {"external_ticket": "FD-123", "description": "Description 1"})

    # Verify that "Category 2" has been created and the item has been moved to it
    assert "Category 2" in meetdown.data["Entity 1"]
    assert meetdown.data["Entity 1"]["Category 1"] == []
    assert meetdown.data["Entity 1"]["Category 2"] == [{"external_ticket": "FD-123", "description": "Description 1"}]

def test_toggle_status_does_nothing_if_item_not_found(meetdown):
    # Set up initial data
    data = {
        "Entity 1": {
            "Category 1": [
                {"external_ticket": "FD-123", "description": "Description 1"}
            ],
            "Category 2": []
        }
    }
    meetdown.data = data

    # Toggle an item that does not exist
    meetdown.toggle_status("Entity 1", "Category 2", "Category 1", {"external_ticket": "FD-456", "description": "Description 2"})

    # Verify that the data remains unchanged
    assert meetdown.data == data

def test_add_item(meetdown):
    # Set up initial data
    meetdown.data = {
        "Entity 1": {
            "Category 1": [],
            "Category 2": []
        }
    }

    # Add a new item to "Category 1"
    meetdown.add_item("Entity 1", "Category 1", "FD-123", "Description 1")

    # Verify that the item has been added to "Category 1"
    assert len(meetdown.data["Entity 1"]["Category 1"]) == 1
    assert meetdown.data["Entity 1"]["Category 1"][0]["external_ticket"] == "FD-123"
    assert meetdown.data["Entity 1"]["Category 1"][0]["description"] == "Description 1"

def test_add_entity(meetdown):
    # Set up initial data
    meetdown.data = {}

    # Add a new entity
    meetdown.add_entity("Entity 1")

    # Verify that the entity has been added with all categories from the config
    assert "Entity 1" in meetdown.data
    assert meetdown.data["Entity 1"] == {
        "⬜": [],
        "✅": []
    }

def test_remove_item(meetdown):
    # Set up initial data
    meetdown.data = {
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
    assert len(meetdown.data["Entity 1"]["Category 1"]) == 1
    assert meetdown.data["Entity 1"]["Category 1"][0]["external_ticket"] == "FD-456"
    assert meetdown.data["Entity 1"]["Category 1"][0]["description"] == "Description 2"

def test_remove_entity(meetdown):
    # Set up initial data
    meetdown.data = {
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
    assert "Entity 1" not in meetdown.data

def test_ensure_default_states_items_exist_in_data(meetdown):
    # Set up initial data with missing ctx items
    meetdown.data = {
        "Entity 1": {
            "⬜": []
        },
        "Entity 2": {
            "⬜": [],
            "✅": []
        }
    }

    # Ensure default ctx items exist
    meetdown.ensure_default_states_items_exist_in_data()

    # Verify that missing ctx items have been added

    assert meetdown.data["Entity 1"]["✅"]
    for entity in meetdown.data:        
      assert "✅" in meetdown.data[entity]
      assert "⬜" in meetdown.data[entity]