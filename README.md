# milhoja

[![image](https://img.shields.io/pypi/v/milhoja.svg)](https://pypi.python.org/pypi/milhoja)

[![image](https://img.shields.io/travis/rmedaer/milhoja.svg)](https://travis-ci.org/rmedaer/milhoja)

[![Documentation Status](https://readthedocs.org/projects/milhoja/badge/?version=latest)](https://milhoja.readthedocs.io/en/latest/?badge=latest)

[![Updates](https://pyup.io/repos/github/rmedaer/milhoja/shield.svg)](https://pyup.io/repos/github/rmedaer/milhoja/)

Milhoja is a tool in top of [Cookiecutter](https://github.com/audreyr/cookiecutter) which maintains
directory templating with Git. The first goal of Milhoja is to provide *upgrade* feature to [Cookiecutter](https://github.com/audreyr/cookiecutter).

## How to ?

Install a [Cookiecutter](https://github.com/audreyr/cookiecutter)
template on current directory:

    milhoja install <your cookiecutter>

Specify a target reference (branch, tag, commit):

    milhoja install -c v1.0.0 <your cookiecutter>

Show installed template:

    milhoja show

Install a [Cookiecutter](https://github.com/audreyr/cookiecutter)
template on your existing Git repository:

    milhoja -C <your repo path> install <your cookiecutter>

Upgrade your repository with last version of template:

    milhoja -C <your repo path> upgrade

## Credits

Code written by Raphael Medaer \<<raphael@medaer.me>\> from an original
idea of Abdó Roig-Maranges \<<abdo.roig@gmail.com>\>

## License

Free software: Apache Software License 2.0