#!/bin/bash

# DoNotePad Build Environment Setup
# This script sets up the virtual environment and builds the application

set -e

echo "🚀 Setting up DoNotePad build environment..."
echo "============================================"

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if python3-venv is installed
if ! python3 -c "import venv" 2>/dev/null; then
    echo -e "${YELLOW}⚠${NC} python3-venv not found. Installing..."
    sudo apt update
    sudo apt install -y python3-venv python3-dev
fi

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo -e "${BLUE}📦${NC} Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
echo -e "${BLUE}🔄${NC} Activating virtual environment..."
source .venv/bin/activate

# Upgrade pip
echo -e "${BLUE}⬆${NC} Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo -e "${BLUE}📦${NC} Installing dependencies..."
pip install -r requirements.txt

# Install build tools
echo -e "${BLUE}🔧${NC} Installing build tools..."
pip install pyinstaller

echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "Now building the application..."
echo ""

# Run the build script with the virtual environment activated
./build.sh
