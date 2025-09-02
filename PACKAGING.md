# DoNotePad - Linux Packaging Guide

This guide explains how to package DoNotePad as a standalone executable for Linux (Ubuntu/Debian).

## 🚀 Quick Start

### Option 1: Build Standalone Executable

```bash
# Install PyInstaller
pip install pyinstaller

# Build the executable
./build.sh
```

The executable will be created at `dist/donotepad` and can be run directly:

```bash
./dist/donotepad
```

### Option 2: Create .deb Package

```bash
# First build the executable
./build.sh

# Then create the .deb package
./create_deb.sh
```

Install the package:

```bash
sudo dpkg -i donotepad_1.0.0_amd64.deb
sudo apt-get install -f  # Fix dependencies if needed
```

## 📋 Prerequisites

### Required Dependencies

- Python 3.8 or higher
- PyInstaller (`pip install pyinstaller`)
- Virtual environment (recommended)

### Optional Dependencies

- **UPX** (for smaller executables): `sudo apt install upx`
- **dpkg-deb** (for .deb packages): Usually pre-installed on Ubuntu/Debian

## 🔨 Build Process

### 1. Standalone Executable

The `build.sh` script:

1. ✅ Checks for virtual environment
2. ✅ Installs PyInstaller if needed
3. ✅ Cleans previous builds
4. ✅ Installs dependencies
5. ✅ Builds executable with PyInstaller
6. ✅ Compresses with UPX (if available)
7. ✅ Tests the executable

**Output**: `dist/donotepad` (standalone executable)

### 2. Debian Package

The `create_deb.sh` script:

1. ✅ Creates proper Debian package structure
2. ✅ Generates control files
3. ✅ Creates desktop entry for applications menu
4. ✅ Includes documentation and copyright
5. ✅ Builds .deb package with `dpkg-deb`

**Output**: `donotepad_1.0.0_amd64.deb` (installable package)

## 📁 Package Contents

### Standalone Executable

- Single file: `donotepad`
- Size: ~50-80MB (includes Python runtime and all dependencies)
- No installation required

### .deb Package

- Executable: `/usr/bin/donotepad`
- Desktop entry: `/usr/share/applications/donotepad.desktop`
- Icon: `/usr/share/pixmaps/donotepad.xpm`
- Documentation: `/usr/share/doc/donotepad/`

## 🚀 Distribution

### For End Users

**Option 1: Standalone Executable**

```bash
# Download and run
chmod +x donotepad
./donotepad
```

**Option 2: .deb Package**

```bash
# Install system-wide
sudo dpkg -i donotepad_1.0.0_amd64.deb

# Run from anywhere
donotepad
```

### For Developers

**Manual Installation**

```bash
# Copy to system PATH
sudo cp dist/donotepad /usr/local/bin/
donotepad
```

## 🔧 Customization

### Modify Package Information

Edit these files to customize:

- `pyproject.toml` - Python package metadata
- `donotepad.spec` - PyInstaller build configuration
- `create_deb.sh` - Debian package details

### Add Custom Icon

Replace the XPM icon in `create_deb.sh` with a proper PNG/SVG icon:

```bash
# Copy your icon
cp your-icon.png donotepad.png

# Update the create_deb.sh script to use PNG instead of XPM
```

## 🐛 Troubleshooting

### Build Issues

**PyInstaller not found:**

```bash
pip install pyinstaller
```

**Missing dependencies:**

```bash
pip install -r requirements.txt
```

**UPX compression fails:**

```bash
sudo apt install upx
# Or disable UPX in build.sh
```

### Runtime Issues

**Executable won't start:**

- Check that all required system libraries are installed
- Run `ldd dist/donotepad` to check dependencies
- Try running with `./dist/donotepad --version`

**Package installation fails:**

```bash
# Check package info
dpkg -I donotepad_1.0.0_amd64.deb

# Force install dependencies
sudo apt-get install -f
```

## 📊 File Sizes

| Package Type          | Typical Size | Notes                      |
| --------------------- | ------------ | -------------------------- |
| Standalone Executable | 50-80MB      | Includes Python runtime    |
| .deb Package          | 50-80MB      | Same executable + metadata |
| Compressed (UPX)      | 20-30MB      | Slower startup time        |

## 🎯 Platform Support

- ✅ Ubuntu 18.04+
- ✅ Debian 10+
- ✅ Linux Mint 19+
- ✅ Elementary OS 5+
- ✅ Pop!\_OS 18.04+

## 📝 License

MIT License - See LICENSE file for details.
