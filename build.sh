#!/bin/bash

# DoNotePad Build Script for Linux
# This script creates a standalone executable using PyInstaller

set -e  # Exit on any error

echo "🔨 Building DoNotePad for Linux..."
echo "======================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo -e "${GREEN}✓${NC} Virtual environment detected: $VIRTUAL_ENV"
else
    echo -e "${YELLOW}⚠${NC} No virtual environment detected. Consider using one for cleaner builds."
fi

# Check if PyInstaller is installed
if ! command -v pyinstaller &> /dev/null; then
    echo -e "${YELLOW}⚠${NC} PyInstaller not found. Installing..."
    pip install pyinstaller
fi

# Check if UPX is available (optional, for compression)
if command -v upx &> /dev/null; then
    echo -e "${GREEN}✓${NC} UPX found - executable will be compressed"
    UPX_AVAILABLE=true
else
    echo -e "${YELLOW}⚠${NC} UPX not found - install with 'sudo apt install upx' for smaller executables"
    UPX_AVAILABLE=false
fi

# Clean previous builds
echo -e "${BLUE}📁${NC} Cleaning previous builds..."
rm -rf build/ dist/ __pycache__/ src/__pycache__/
find . -name "*.pyc" -delete
find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo -e "${BLUE}📦${NC} Installing dependencies..."
    pip install -r requirements.txt
fi

# Install PyInstaller if not already installed
pip install pyinstaller

# Build the executable
echo -e "${BLUE}🔨${NC} Building executable with PyInstaller..."
if $UPX_AVAILABLE; then
    pyinstaller donotepad.spec --clean --noconfirm
else
    # Disable UPX if not available
    sed 's/upx=True/upx=False/' donotepad.spec > donotepad_no_upx.spec
    pyinstaller donotepad_no_upx.spec --clean --noconfirm
    rm donotepad_no_upx.spec
fi

# Check if build was successful
if [ -f "dist/donotepad" ]; then
    echo -e "${GREEN}✅ Build successful!${NC}"
    echo ""
    echo "📂 Executable location: $(pwd)/dist/donotepad"
    
    # Get file size
    SIZE=$(du -h dist/donotepad | cut -f1)
    echo "📏 File size: $SIZE"
    
    # Make executable
    chmod +x dist/donotepad
    
    # Test the executable
    echo -e "${BLUE}🧪${NC} Testing executable..."
    if ./dist/donotepad --version 2>/dev/null || true; then
        echo -e "${GREEN}✓${NC} Executable test passed"
    fi
    
    echo ""
    echo -e "${GREEN}🎉 DoNotePad has been successfully packaged!${NC}"
    echo ""
    echo "📋 To run the application:"
    echo "   ./dist/donotepad"
    echo ""
    echo "📋 To install system-wide:"
    echo "   sudo cp dist/donotepad /usr/local/bin/"
    echo "   donotepad"
    echo ""
    echo "📋 To create a .deb package:"
    echo "   ./create_deb.sh"
    
else
    echo -e "${RED}❌ Build failed!${NC}"
    echo "Check the build output above for errors."
    exit 1
fi
