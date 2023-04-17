```
███    ███ ███████ ███████ ████████ ██████   ██████  ██     ██ ███    ██
████  ████ ██      ██         ██    ██   ██ ██    ██ ██     ██ ████   ██
██ ████ ██ █████   █████      ██    ██   ██ ██    ██ ██  █  ██ ██ ██  ██
██  ██  ██ ██      ██         ██    ██   ██ ██    ██ ██ ███ ██ ██  ██ ██
██      ██ ███████ ███████    ██    ██████   ██████   ███ ███  ██   ████
```

## Prerequisites

* Python 3.6+

## Getting Started

```
pip install -r requirements.txt
```

Add aliases to shell profile to load .env in pwd
```
alias source_env='if [ -f .env ]; then source .env; else echo ".env file not found"; fi'
alias md="source_env && python /path/to/md.py"
```

```
cp .env-example .env

source .env
```

## Run

```
python md.py
#or
chmod +x /path/to/md.py
./path/to/md.py
```
