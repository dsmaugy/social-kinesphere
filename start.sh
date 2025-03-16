#!/bin/bash

git pull
poetry_bin=$(which poetry)
$poetry_bin run python projections.py
