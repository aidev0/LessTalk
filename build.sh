#!/bin/bash

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install required libraries
pip install requests python-dotenv

# Done
echo "✅ Virtual environment set up and dependencies installed."
