#!/bin/bash
rm -rf venv
virtualenv venv
pip3 install ipython numpy scipy bokeh pandas
pip3 install cvxpy
echo activate with: source/venv/activate

