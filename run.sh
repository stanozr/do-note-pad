#!/bin/bash
# DoNotePad Flet Version Launcher Script

# Get the directory where this script is located
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the project directory
cd "$DIR"

# Run the Flet application using the virtual environment Python
./.venv/bin/python main.py
