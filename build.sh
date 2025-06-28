#!/bin/bash
# Exit immediately if a command exits with non-zero status
set -e

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate

# Install requirements
pip install --upgrade pip
pip install wheel setuptools
pip install -r requirements.txt