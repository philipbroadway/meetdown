```
┌┬┐┌─┐┌─┐┌┬┐┌┬┐┌─┐┬ ┬┌┐┌
│││├┤ ├┤  │  │││ │││││││
┴ ┴└─┘└─┘ ┴ ─┴┘└─┘└┴┘┘└┘
```
> Markdown editor for meetups

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
#or
chmod +x /path/to/meetdown.py
./path/to/meetdown.py
```

## Docker

Quickstart:
```bash
docker-compose run meetdown

```

To open the folder where the markdown documents are kept, you can use the following command:

```bash
docker-compose exec md /bin/bash -c "cd /meetdown/ && ls -l"
```