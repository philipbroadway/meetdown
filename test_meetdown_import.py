import pytest
import os
from .meetdown import MeetDown

@pytest.fixture
def tmp_file(tmp_path):
    filename = tmp_path / "test_meetdown.md"
    yield filename
    if os.path.exists(filename):
        os.remove(filename)

def test_save_and_load(tmp_file):
    config = MeetDown.default_config()
    meetdown = MeetDown(config)
    meetdown.md_data = {
        "Entity1": {
            "Category1": [
                {"external_ticket": "TICKET1", "description": "Item1"},
                {"external_ticket": "TICKET2", "description": "Item2"},
            ]
        },
        "Entity2": {
            "Category2": [
                {"external_ticket": "TICKET3", "description": "Item3"},
                {"external_ticket": "TICKET4", "description": "Item4"},
            ]
        }
    }

    meetdown.write(tmp_file)

    # Create a new instance of MeetDown and load the data from the file
    new_meetdown = MeetDown(config)
    new_meetdown.load_from_markdown(tmp_file)

    # Verify the loaded data matches the original data
    print(f"new_meetdown.md_data: {new_meetdown.md_data.items()}")
    print(f"meetdown.md_data: {meetdown.md_data.items()}")
    assert new_meetdown.md_data.items() == meetdown.md_data.items()
