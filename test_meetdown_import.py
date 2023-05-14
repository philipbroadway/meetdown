import pytest
from meetdown import MeetDown

@pytest.fixture
def meetdown():
    config = MeetDown.default_config()
    return MeetDown(config)

def test_generate_options(meetdown):
    # Test the generate_options() method
    expected_options = "1. Add\n2. Remove\n3. Toggle\n4. Load\n5. Save & Quit"
    options = meetdown.generate_options()
    assert options == expected_options

def test_itemTypes(meetdown):
    # Test the itemTypes() method
    expected_types = ["⬜", "✅"]
    types = meetdown.itemTypes()
    assert types == expected_types

def test_add(meetdown):
    # Test the add() method
    meetdown.add()
    # Add assertions to verify the expected changes in meetdown.md_data

def test_remove(meetdown):
    # Test the remove() method
    meetdown.remove()
    # Add assertions to verify the expected changes in meetdown.md_data

def test_toggle(meetdown):
    # Test the toggle() method
    meetdown.toggle()
    # Add assertions to verify the expected changes in meetdown.md_data