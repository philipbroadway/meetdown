```
┌┬┐┌─┐┌─┐┌┬┐┌┬┐┌─┐┬ ┬┌┐┌
│││├┤ ├┤  │  │││ │││││││
┴ ┴└─┘└─┘ ┴ ─┴┘└─┘└┴┘┘└┘
```

## Prerequisites

* Python 3.6+

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
docker build -t md . && docker run -it md

```

To open the folder where the markdown documents are kept, you can use the following command:

```bash
docker-compose exec md /bin/bash -c "cd /meetdown/ && ls -l"
```