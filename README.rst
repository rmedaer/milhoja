===============================
milhoja
===============================

.. image:: https://img.shields.io/pypi/v/milhoja.svg
        :target: https://pypi.python.org/pypi/milhoja

.. image:: https://img.shields.io/travis/rmedaer/milhoja.svg
        :target: https://travis-ci.org/rmedaer/milhoja

.. image:: https://readthedocs.org/projects/milhoja/badge/?version=latest
        :target: https://milhoja.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/rmedaer/milhoja/shield.svg
     :target: https://pyup.io/repos/github/rmedaer/milhoja/
     :alt: Updates

.. _Cookiecutter: https://github.com/audreyr/cookiecutter

Milhoja is a tool in top of Cookiecutter_ which maintains directory templating
with Git. The first goal of Milhoja is to provide *upgrade* feature to Cookiecutter_.

How to ?
--------

Install a Cookiecutter_ template on current directory:

.. code-block::

   milhoja install <your cookiecutter>

Specify a target reference (branch, tag, commit):

.. code-block::

   milhoja install -c v1.0.0 <your cookiecutter>

Show installed template:

.. code-block::

   milhoja show

Install a Cookiecutter_ template on your existing Git repository:

.. code-block::

   milhoja -C <your repo path> install <your cookiecutter>

Upgrade your repository with last version of template:

.. code-block::

   milhoja -C <your repo path> upgrade


Credits
-------

Code written by Raphael Medaer <raphael@medaer.me>
from an original idea of Abdó Roig-Maranges <abdo.roig@gmail.com>

License
-------

Free software: Apache Software License 2.0
