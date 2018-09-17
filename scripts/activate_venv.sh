#!/usr/bin/env bash

echo "activating depot_env"
#source "/home/hareram/python-environments/depot_env/bin/activate"
x = $(cd $(dirname "$1") && pwd -P)/$(basename "$1")
/bin/bash -c ". depot_env/bin/activate"
