#!/bin/bash
rm -rf venv
virtualenv venv
pip install ipython numpy scipy bokeh pandas
pip install xlsx2csv
echo activate with: source/venv/activate

