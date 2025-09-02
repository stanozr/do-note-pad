# 📦 DoNotePad - Linux Distribution Files

DoNotePad has been successfully packaged for Linux (Ubuntu/Debian) distribution!

## 📋 Available Packages

### 1. Standalone Executable

- **File**: `dist/donotepad`
- **Size**: ~11MB
- **Description**: Single-file executable that runs on any Linux system
- **No installation required**

### 2. Debian Package (.deb)

- **File**: `donotepad_1.0.0_amd64.deb`
- **Size**: ~11MB
- **Description**: Standard Debian package for Ubuntu/Debian systems
- **Includes desktop integration**

## 🚀 Installation Options

### Option 1: Run Standalone Executable

```bash
# Make executable (if needed)
chmod +x dist/donotepad

# Run directly
./dist/donotepad
```

### Option 2: Install .deb Package

```bash
# Install the package
sudo dpkg -i donotepad_1.0.0_amd64.deb

# Fix dependencies if needed
sudo apt-get install -f

# Run from anywhere
donotepad
```

### Option 3: Install to System PATH

```bash
# Copy executable to system PATH
sudo cp dist/donotepad /usr/local/bin/

# Run from anywhere
donotepad
```

## ✨ Features Included

- ✅ **Todo.txt Format Support** - Full compatibility with todo.txt standard
- ✅ **Markdown Notes** - Rich text notes with live preview
- ✅ **Keyboard Shortcuts** - Power-user shortcuts (Ctrl+N, Ctrl+T, Ctrl+Enter, ESC)
- ✅ **Material Design UI** - Beautiful, modern interface
- ✅ **Cross-Platform Data** - Plain text files work everywhere
- ✅ **No Database Required** - Simple file-based storage

## 🔧 System Requirements

- **OS**: Ubuntu 18.04+, Debian 10+, or compatible Linux distribution
- **Architecture**: x86_64 (64-bit)
- **Dependencies**: GTK3 libraries (usually pre-installed)
- **Disk Space**: ~15MB after installation

## 📋 Package Contents

### Standalone Executable

```
donotepad                    # Main executable (11MB)
```

### .deb Package

```
/usr/bin/donotepad                           # Main executable
/usr/share/applications/donotepad.desktop    # Desktop entry
/usr/share/pixmaps/donotepad.xpm            # Application icon
/usr/share/doc/donotepad/                   # Documentation
```

## 🎯 Desktop Integration

After installing the .deb package:

- ✅ **Applications Menu**: Find DoNotePad in Office/Utilities
- ✅ **Desktop Entry**: Launch from desktop or file manager
- ✅ **Command Line**: Run `donotepad` from any terminal
- ✅ **File Associations**: Can be set as default for .txt files

## 🔄 Updating

### Standalone Executable

Replace the file with a newer version:

```bash
# Download new version
wget https://releases.example.com/donotepad-latest

# Replace old version
mv donotepad-latest dist/donotepad
chmod +x dist/donotepad
```

### .deb Package

Install new package over the old one:

```bash
sudo dpkg -i donotepad_1.1.0_amd64.deb
```

## 🗑️ Uninstalling

### Standalone Executable

Simply delete the file:

```bash
rm dist/donotepad
# or if installed to system:
sudo rm /usr/local/bin/donotepad
```

### .deb Package

```bash
sudo apt remove donotepad
```

## 🛠️ Building from Source

If you want to build your own package:

```bash
# Setup environment
./setup_and_build.sh

# Or manually:
source .venv/bin/activate
./build.sh
./create_deb.sh
```

## 📞 Support

- **Issues**: Report bugs or request features
- **Documentation**: See PACKAGING.md for detailed build instructions
- **Data**: Your todos and notes are stored in plain text files
- **Backup**: Simply copy your data folder to backup everything

## 📄 License

MIT License - You're free to use, modify, and distribute DoNotePad.

---

**DoNotePad v1.0.0** - A beautiful, lightweight productivity app for managing todos and notes.

_Built with ❤️ using Python and Flet_
