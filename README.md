# pysqlx

![Publish](https://github.com/pysqlx/pysqlx/workflows/Publish/badge.svg)
![Test](https://github.com/pysqlx/pysqlx/workflows/Test/badge.svg)
[![Downloads](https://static.pepy.tech/personalized-badge/pysqlx?period=week&units=international_system&left_color=black&right_color=orange&left_text=Last%20Week)](https://pepy.tech/project/pysqlx)
[![Downloads](https://static.pepy.tech/personalized-badge/pysqlx?period=month&units=international_system&left_color=black&right_color=orange&left_text=Month)](https://pepy.tech/project/pysqlx)
[![Downloads](https://static.pepy.tech/personalized-badge/pysqlx?period=total&units=international_system&left_color=black&right_color=orange&left_text=Total)](https://pepy.tech/project/pysqlx)

A generic SQL driver package.

## Installation

To install `pysqlx` into your Python environment:

    pip install -U pysqlx

## Usage

## Development

To clone the library for development:

    git clone https://github.com/pysqlx/pysqlx.git

or

    git clone git@github.com:pysqlx/pysqlx.git

### Build The Virtual Environment

The current earliest Python version supported is `3.9`. You need to be able to create a virtual environment at this version to make sure any changes you make is compatible.

If you are using `conda`:

    conda create --prefix=.venv python=3.9 --yes

If you are using `venv`, make sure you have the right base package:

    >> python --version
    Python 3.9.x

Once you verify your base Python, you can then create a virtual environment using:

    virtualenv -p py3.9 .venv

### Setup

Once you have created your virtual environment and made sure it is active in your current command line:

    python3 -m pip install --upgrade pip
    pip install -e .[dev]

This should all the dependencies you need for developing into the library and also allow you to run the unit tests:

    pytest
