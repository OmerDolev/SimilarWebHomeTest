#!/bin/bash

# entering python virtual env
source ./env/bin/activate

# running flask app
FLASK_APP=./main.py flask run --host=0.0.0.0 --port=8080
