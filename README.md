```
┌┬┐┌─┐┌─┐┌┬┐┌┬┐┌─┐┬ ┬┌┐┌
│││├┤ ├┤  │  │││ │││││││
┴ ┴└─┘└─┘ ┴ ─┴┘└─┘└┴┘┘└┘
```
> markdown editor for mtg's

[![Pytest](https://github.com/frontdesk/meetdown/actions/workflows/pytest.yml/badge.svg)](https://github.com/frontdesk/meetdown/actions/workflows/pytest.yml)

## Prerequisites

* [Python 3+](https://github.com/frontdesk/meetdown/blob/main/python_installation_guide.md)

--or--  

* Docker

## Getting Started

### Run locally

If you don't have Python installed, follow [Python installation](https://github.com/frontdesk/meetdown/blob/main/python_installation_guide.md) guide.

```bash
# Install dependencies
cd meetdown && pip install -r requirements.txt

# Running app
python meetdown.py
```

#### Meeting example

```
python meetdown.py --entities person1,person2,someBiz1,someBiz2
```

#### Standup example

```
python meetdown.py --entities "↪️ -Previous,📅-Today,🗂️ -Backlog"'
```

### Run in Docker

Run App:
```bash
cd meetdown && docker-compose run meetdown

```

## Testing

```bash
pytest
```
