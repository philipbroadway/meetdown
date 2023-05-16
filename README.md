```
┌┬┐┌─┐┌─┐┌┬┐┌┬┐┌─┐┬ ┬┌┐┌
│││├┤ ├┤  │  │││ │││││││
┴ ┴└─┘└─┘ ┴ ─┴┘└─┘└┴┘┘└┘
```
> Markdown editor for meetups

[![Pytest](https://github.com/frontdesk/meetdown/actions/workflows/pytest.yml/badge.svg)](https://github.com/frontdesk/meetdown/actions/workflows/pytest.yml)

## Prerequisites

* Python 3 >= 3.6
* panflute
* bs4
* redis
* pytest 

`--or--` 

* Docker

## Getting Started

```bash
cd markdown && python meetdown.py
```

## Docker

Quickstart:
```bash
cd markdown && docker-compose run meetdown

```

## Testing

```bash
pytest
```
