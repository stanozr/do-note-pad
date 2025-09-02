#!/bin/bash

# DoNotePad Icon Generator Script
# Converts SVG icon to various formats needed for Linux packaging

set -e

echo "🎨 Generating DoNotePad icons..."
echo "================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Check if Inkscape is available
if command -v inkscape &> /dev/null; then
    echo -e "${GREEN}✓${NC} Inkscape found - using for high-quality conversion"
    CONVERTER="inkscape"
elif command -v convert &> /dev/null; then
    echo -e "${YELLOW}⚠${NC} ImageMagick found - using convert (install inkscape for better quality)"
    CONVERTER="imagemagick"
else
    echo -e "${YELLOW}⚠${NC} Neither Inkscape nor ImageMagick found. Installing imagemagick..."
    sudo apt update
    sudo apt install -y imagemagick
    CONVERTER="imagemagick"
fi

# Create assets directory if it doesn't exist
mkdir -p assets

# SVG source file
SVG_FILE="assets/donotepad.svg"

if [ ! -f "$SVG_FILE" ]; then
    echo -e "${YELLOW}⚠${NC} SVG file not found at $SVG_FILE"
    exit 1
fi

echo -e "${BLUE}📁${NC} Creating icon directories..."
mkdir -p assets/icons/hicolor/{16x16,22x22,24x24,32x32,48x48,64x64,96x96,128x128,256x256,512x512}/apps
mkdir -p assets/icons/pixmaps

# Function to generate PNG with Inkscape
generate_png_inkscape() {
    local size=$1
    local output=$2
    inkscape --export-type=png --export-width=$size --export-height=$size --export-filename="$output" "$SVG_FILE" >/dev/null 2>&1
}

# Function to generate PNG with ImageMagick
generate_png_imagemagick() {
    local size=$1
    local output=$2
    convert -background transparent -size ${size}x${size} "$SVG_FILE" "$output"
}

# Generate PNG function based on available converter
generate_png() {
    if [ "$CONVERTER" == "inkscape" ]; then
        generate_png_inkscape "$1" "$2"
    else
        generate_png_imagemagick "$1" "$2"
    fi
}

echo -e "${BLUE}🖼${NC} Generating PNG icons..."

# Generate various sizes for hicolor theme
sizes=(16 22 24 32 48 64 96 128 256 512)

for size in "${sizes[@]}"; do
    echo -e "   ${size}x${size}..."
    generate_png $size "assets/icons/hicolor/${size}x${size}/apps/donotepad.png"
done

# Generate pixmap version (48x48 is standard for pixmaps)
echo -e "${BLUE}📋${NC} Generating pixmap..."
generate_png 48 "assets/icons/pixmaps/donotepad.png"

# Generate ICO file for potential Windows compatibility
if command -v convert &> /dev/null; then
    echo -e "${BLUE}🖼${NC} Generating ICO file..."
    convert assets/icons/hicolor/16x16/apps/donotepad.png \
            assets/icons/hicolor/32x32/apps/donotepad.png \
            assets/icons/hicolor/48x48/apps/donotepad.png \
            assets/icons/hicolor/256x256/apps/donotepad.png \
            assets/donotepad.ico
fi

# Generate XPM format (for older systems)
if command -v convert &> /dev/null; then
    echo -e "${BLUE}🎨${NC} Generating XPM file..."
    convert assets/icons/hicolor/48x48/apps/donotepad.png assets/icons/pixmaps/donotepad.xpm
fi

# Create a copy for the main assets directory
cp assets/icons/hicolor/128x128/apps/donotepad.png assets/donotepad.png

echo -e "${GREEN}✅ Icon generation complete!${NC}"
echo ""
echo "📁 Generated files:"
echo "   SVG: assets/donotepad.svg"
echo "   PNG: assets/donotepad.png (128x128)"
echo "   ICO: assets/donotepad.ico"
echo "   XPM: assets/icons/pixmaps/donotepad.xpm"
echo "   Hicolor theme: assets/icons/hicolor/*/apps/donotepad.png"
echo ""
echo "📋 Usage:"
echo "   • Copy to /usr/share/icons/hicolor/ for system-wide themes"
echo "   • Use assets/donotepad.png for applications"
echo "   • Use assets/donotepad.ico for PyInstaller --icon parameter"
echo "   • Use assets/icons/pixmaps/donotepad.xpm for .deb packages"
