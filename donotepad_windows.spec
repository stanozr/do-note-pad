# -*- mode: python ; coding: utf-8 -*-

import os

block_cipher = None

# Data files to include
datas = [
    ('test_data', 'test_data'),
]

# Hidden imports for Flet
hiddenimports = [
    'flet',
    'flet.core',
    'flet.core.page',
    'flet.utils',
    'dateutil',
    'dateutil.parser',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='donotepad',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/donotepad.ico',
    version_file=None,  # We can add a version file later
)
