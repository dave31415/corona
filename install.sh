#!/bin/bash
rm -rf venv
virtualenv venv
pip install ipython numpy scipy bokeh pandas
echo activate with: source/venv/activate

