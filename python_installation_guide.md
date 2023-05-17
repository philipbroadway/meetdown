# Installing Python

## Prerequisites

- [ ] Ensure you have a C compiler and the OpenSSL library installed on your system

- [ ] Mac users can install OpenSSL using [Homebrew](https://brew.sh/)

- [ ] Windows users can install OpenSSL using [Chocolatey](https://chocolatey.org/)

- [ ] Linux users can install OpenSSL using their package manager (yum, apt, etc)

### Linux/macOS

    * Install pyenv using pyenv-installer:
        Run in Terminal: `curl https://pyenv.run | bash`
    * Configure shell to use pyenv:
        * For Bash, add to ~/.bashrc: export PATH="$HOME/.pyenv/bin:$PATH"
        * For Zsh, add to ~/.zshrc: export PATH="$HOME/.pyenv/bin:$PATH"
        * Add to shell configuration file: eval "$(pyenv init --path)"
    * Restart shell or open a new Terminal window to apply changes.
    * Install Python version using pyenv:
        * Run: `pyenv install {version}`
    Set the installed version as the global default:
        Run: pyenv global {version}

### Windows

    * Install pyenv-win using pip:
        * Run in Command Prompt: `pip install pyenv-win --target $HOME\\.pyenv`
    * Add pyenv to PATH:
        * Run: `setx /M PATH "%PATH%;%HOME%\\.pyenv\\pyenv-win\\bin;%HOME%\\.pyenv\\pyenv-win\\shims"`
    * Restart Command Prompt to apply changes.
    * Install Python version using pyenv:
        * Run: `pyenv install {version}`
    * Set the installed version as the global default:
        * Run: `pyenv global {version}`
