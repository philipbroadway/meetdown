```
┌┬┐┌─┐┌─┐┌┬┐┌┬┐┌─┐┬ ┬┌┐┌
│││├┤ ├┤  │  │││ │││││││
┴ ┴└─┘└─┘ ┴ ─┴┘└─┘└┴┘┘└┘
```
> Markdown editor for meetups

[![Pytest](https://github.com/frontdesk/meetdown/actions/workflows/pytest.yml/badge.svg)](https://github.com/frontdesk/meetdown/actions/workflows/pytest.yml)

## Prerequisites

* Python 3 >= 3.6

--or--  

* Docker

## Getting Started

```bash
# Install dependencies
cd meetdown && pip install -r requirements.txt

# Running app
python meetdown.py
```

## Docker

Quickstart:
```bash
cd meetdown && docker-compose run meetdown

```

## Testing

```bash
pytest
```
