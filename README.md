```
┌┬┐┌─┐┌─┐┌┬┐┌┬┐┌─┐┬ ┬┌┐┌
│││├┤ ├┤  │  │││ │││││││
┴ ┴└─┘└─┘ ┴ ─┴┘└─┘└┴┘┘└┘
```
> Markdown editor for meetups

## Prerequisites

* Python 3 >= 3.6
* requests
* python-dotenv
* beautifulsoup4
* unitest
* panflute
--or--
* Docker

## Getting Started

```bash
python md.py
#or
chmod +x /path/to/md.py
./path/to/md.py
```

## Docker

Quickstart:
```bash
docker-compose run app

```

To open the folder where the markdown documents are kept, you can use the following command:

```bash
docker-compose exec md /bin/bash -c "cd /meetdown/ && ls -l"
```