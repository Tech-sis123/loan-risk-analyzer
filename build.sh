#!/bin/bash
set -e  # Exit immediately if any command fails

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install build essentials
#pip install --upgrade pip setuptools wheel

# Install requirements
pip install -r requirements.txt