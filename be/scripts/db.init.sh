#!/bin/bash

poetry run python cli.py db load poi
poetry run python cli.py db load road
poetry run python cli.py db load address