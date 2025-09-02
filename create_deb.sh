#!/bin/bash

# Create .deb package for DoNotePad
# This script creates a Debian package for easy installation on Ubuntu/Debian

set -e

echo "📦 Creating .deb package for DoNotePad..."
echo "=========================================="

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m'

# Package information
PACKAGE_NAME="donotepad"
VERSION="1.0.1"
ARCHITECTURE="amd64"
MAINTAINER="DoNotePad Team <contact@donotepad.com>"
DESCRIPTION="A beautiful, lightweight productivity app for managing todos and notes"

# Check if executable exists
if [ ! -f "dist/donotepad" ]; then
    echo -e "${RED}❌ Executable not found!${NC}"
    echo "Please run './build.sh' first to create the executable."
    exit 1
fi

# Create package directory structure
PACKAGE_DIR="${PACKAGE_NAME}_${VERSION}_${ARCHITECTURE}"
rm -rf "$PACKAGE_DIR"
mkdir -p "$PACKAGE_DIR"/{DEBIAN,usr/bin,usr/share/applications,usr/share/pixmaps,usr/share/doc/donotepad}

echo -e "${BLUE}📁${NC} Creating package structure..."

# Copy executable
cp dist/donotepad "$PACKAGE_DIR/usr/bin/"
chmod +x "$PACKAGE_DIR/usr/bin/donotepad"

# Create control file
cat > "$PACKAGE_DIR/DEBIAN/control" << EOF
Package: $PACKAGE_NAME
Version: $VERSION
Architecture: $ARCHITECTURE
Maintainer: $MAINTAINER
Depends: libc6, libgtk-3-0
Section: utils
Priority: optional
Homepage: https://github.com/donotepad/donotepad
Description: $DESCRIPTION
 DoNotePad is a modern, beautiful productivity application that helps you
 manage your todos and notes efficiently. It supports the todo.txt format
 and provides a clean, intuitive interface built with Material Design.
 .
 Features:
  * Todo.txt format support with priorities and due dates
  * Markdown notes with live preview
  * Beautiful Material Design interface
  * Plain text storage (no database)
  * Keyboard shortcuts for power users
  * Cross-platform compatibility
EOF

# Create desktop entry
cat > "$PACKAGE_DIR/usr/share/applications/donotepad.desktop" << EOF
[Desktop Entry]
Name=DoNotePad
Comment=Todo and Notes Manager
Exec=/usr/bin/donotepad
Icon=/usr/share/pixmaps/donotepad.png
Type=Application
Categories=Office;Utility;
Keywords=todo;notes;productivity;tasks;
StartupNotify=true
EOF

# Copy custom icon
cp assets/donotepad.png "$PACKAGE_DIR/usr/share/pixmaps/"

# Copy documentation
cp README.md "$PACKAGE_DIR/usr/share/doc/donotepad/" 2>/dev/null || echo "# DoNotePad" > "$PACKAGE_DIR/usr/share/doc/donotepad/README.md"

# Create copyright file
cat > "$PACKAGE_DIR/usr/share/doc/donotepad/copyright" << EOF
Format: https://www.debian.org/doc/packaging-manuals/copyright-format/1.0/
Upstream-Name: donotepad
Source: https://github.com/donotepad/donotepad

Files: *
Copyright: 2025 DoNotePad Team
License: MIT

License: MIT
 Permission is hereby granted, free of charge, to any person obtaining a
 copy of this software and associated documentation files (the "Software"),
 to deal in the Software without restriction, including without limitation
 the rights to use, copy, modify, merge, publish, distribute, sublicense,
 and/or sell copies of the Software, and to permit persons to whom the
 Software is furnished to do so, subject to the following conditions:
 .
 The above copyright notice and this permission notice shall be included
 in all copies or substantial portions of the Software.
 .
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
 OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
 THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
 FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
 DEALINGS IN THE SOFTWARE.
EOF

# Create postinst script
cat > "$PACKAGE_DIR/DEBIAN/postinst" << EOF
#!/bin/bash
set -e

# Update desktop database
if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database /usr/share/applications
fi

echo "DoNotePad has been installed successfully!"
echo "You can now run it from the applications menu or by typing 'donotepad' in terminal."
EOF

chmod +x "$PACKAGE_DIR/DEBIAN/postinst"

# Create prerm script
cat > "$PACKAGE_DIR/DEBIAN/prerm" << EOF
#!/bin/bash
set -e

echo "Removing DoNotePad..."
EOF

chmod +x "$PACKAGE_DIR/DEBIAN/prerm"

# Build the package
echo -e "${BLUE}🔨${NC} Building .deb package..."
dpkg-deb --build "$PACKAGE_DIR"

if [ -f "${PACKAGE_DIR}.deb" ]; then
    echo -e "${GREEN}✅ Package created successfully!${NC}"
    echo ""
    echo "📦 Package: ${PACKAGE_DIR}.deb"
    
    # Get package size
    SIZE=$(du -h "${PACKAGE_DIR}.deb" | cut -f1)
    echo "📏 Package size: $SIZE"
    
    echo ""
    echo -e "${GREEN}🎉 DoNotePad .deb package created!${NC}"
    echo ""
    echo "📋 To install:"
    echo "   sudo dpkg -i ${PACKAGE_DIR}.deb"
    echo "   sudo apt-get install -f  # if there are dependency issues"
    echo ""
    echo "📋 To uninstall:"
    echo "   sudo apt remove $PACKAGE_NAME"
    
    # Clean up build directory
    rm -rf "$PACKAGE_DIR"
    
else
    echo -e "${RED}❌ Package creation failed!${NC}"
    exit 1
fi
