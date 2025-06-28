#!/bin/bash
set -e  # Exit immediately if any command fails

# Use the environment provided by Render
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
