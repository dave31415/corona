#!/bin/bash
rm -rf venv
virtualenv venv
pip3 install ipython numpy scipy bokeh pandas
pip3 install xlsx2csv, cvxpy
echo activate with: source/venv/activate

