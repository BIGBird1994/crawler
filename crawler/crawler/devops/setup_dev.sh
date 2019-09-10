#!/usr/bin/env bash

#cd ..
python3 -m pip install --user virtualenv
python3 -m virtualenv env
source  env/bin/activate
pip3 install -r requirements.txt
python --version


########  will automate the following later #########
#
#VENV_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"
## VENV_DIR="/Users/xiaoxizhang/PycharmProjects/wolverine"
#echo "$VENV_DIR/env/bin/activate"
#
## activates the newly created virtual environment
#. "${VENV_DIR}"/env/bin/activate
#
## /bin/bash -c ". $VENV_DIR/env/bin/activate; exec /bin/bash -i"
## source $CURR_DIR/env/bin/activate
#
## pip3 install --user -r requirements.txt
#cd ..
#pip3 install  -r $VENV_DIR/requirements.txt
#
#python --version
#
#
######### let's do it manually for now #########
#
#python3 -m pip install --user virtualenv
#python3 -m virtualenv env
#source  .env/bin/activate
## pip3 install --user -r requirements.txt
#pip3 install -r requirements.txt
#python --version

