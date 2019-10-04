# milhoja

[![image](https://img.shields.io/pypi/v/milhoja.svg)](https://pypi.python.org/pypi/milhoja)

[![image](https://img.shields.io/travis/rmedaer/milhoja.svg)](https://travis-ci.org/rmedaer/milhoja)

Milhoja is a tool in top of [Cookiecutter](https://github.com/audreyr/cookiecutter) which maintains
directory templating with Git. The first goal of Milhoja is to provide *upgrade* feature to [Cookiecutter](https://github.com/audreyr/cookiecutter).

## Usage

Install a [Cookiecutter](https://github.com/audreyr/cookiecutter)
template on current directory:

    ```bash
    milhoja install <your cookiecutter>
    ```

Specify a target reference (branch, tag, commit):

    ```bash
    milhoja install -c v1.0.0 <your cookiecutter>
    ```

Show installed template:

    ```bash
    milhoja show
    ```

Install a [Cookiecutter](https://github.com/audreyr/cookiecutter) template on your existing Git repository:

    ```bash
    milhoja -C <your repo path> install <your cookiecutter>
    ```

Upgrade your repository with last version of template:

    ```bash
    milhoja -C <your repo path> upgrade
    ```

## Credits

[Original code](https://github.com/rmedaer/milhoja) written by [Raphael Medaer](https://github.com/rmedaer) from an [original
idea](https://github.com/cookiecutter/cookiecutter/issues/784) of [Abdó Roig-Maranges](https://github.com/aroig).

## License

Free software: Apache Software License 2.0
