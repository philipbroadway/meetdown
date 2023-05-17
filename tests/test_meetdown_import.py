import pytest
import os
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from meetdown import MeetDown

markdown_examples = [
"""
## Red
| Category | Jira Ticket | Description |
|----------|-------------|-------------|
| ✅ | [fd-12][fd-12-ref] | test |



[fd-12-ref]: https://frontdeskhq.atlassian.net/jira/software/c/projects/FD/boards/7/backlog?view=detail&selectedIssue=fd-12
""",
"""
## Test 1
| Category | Jira Ticket | Description |
|----------|-------------|-------------|
| ✅ |  | No ticket |
## Test 2
| Category | Jira Ticket | Description |
|----------|-------------|-------------|
| ⬜ | [op-1][op-1-ref] | Has ticket |
| ✅ | [op-6][op-6-ref] | has ticket too |


[op-1-ref]: https://some.other.tracker.com?selcted==op-1
[op-6-ref]: https://some.other.tracker.com?selcted==op-6

"""
]


@pytest.fixture
def tmp_file(tmp_path):
    filename = tmp_path / "test_meetdown.md"
    yield filename
    if os.path.exists(filename):
        os.remove(filename)

def test_exported_data_imports_and_exports(tmp_file):
    config = MeetDown.default_config()
    meetdown = MeetDown(config)

    for markdown in markdown_examples:
      with open(tmp_file, 'w') as file:
        file.write(markdown)

      meetdown.load_from_markdown(tmp_file)

      # Verify the loaded data matches the original data
      assert meetdown.data.items() == meetdown.data.items()
