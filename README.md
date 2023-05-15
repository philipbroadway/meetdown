```
┌┬┐┌─┐┌─┐┌┬┐┌┬┐┌─┐┬ ┬┌┐┌
│││├┤ ├┤  │  │││ │││││││
┴ ┴└─┘└─┘ ┴ ─┴┘└─┘└┴┘┘└┘
```
> Markdown editor for meetups

[![Tests](https://github.com/frontdesk/meetdown/actions/workflows/python-app.yml/badge.svg?branch=main)](https://github.com/frontdesk/meetdown/actions/workflows/python-app.yml)

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
python meetdown.py
```

## Docker

Quickstart:
```bash
docker-compose run meetdown

```

To open the folder where the markdown documents are kept, you can use the following command:

```bash
docker-compose exec meetdown /bin/bash -c "cd /meetdown/ && ls -l"
```