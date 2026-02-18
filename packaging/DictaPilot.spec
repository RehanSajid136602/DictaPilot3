# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for DictaPilot
Build single-file executables for Windows, macOS, and Linux

Usage:
    pyinstaller packaging/DictaPilot.spec
"""

import os
from pathlib import Path

block_cipher = None

# Get the project root directory (SPECPATH is defined by PyInstaller)
try:
    project_root = Path(SPECPATH).parent.resolve()
except NameError:
    project_root = Path(os.getcwd()).resolve()

# Data files to include
datas = [
    (str(project_root / ".env.example"), "."),
    (str(project_root / "public" / "asset" / "logo.png"), "public/asset"),
]

# Check if logo exists, add to datas if present
logo_path = project_root / "Dictepilot.png"
if logo_path.exists():
    datas.append((str(logo_path), "."))

a = Analysis(
    [str(project_root / "app.py")],
    pathex=[str(project_root)],
    binaries=[],
    datas=datas,
    hiddenimports=[
        # Core audio dependencies
        'sounddevice',
        'soundfile',
        'numpy',
        
        # API client
        'groq',
        
        # Hotkey dependencies
        'keyboard',
        'pynput',
        'pynput.keyboard',
        'pynput.mouse',
        
        # Configuration
        'dotenv',
        
        # Clipboard
        'pyperclip',
        
        # PySide6 - all required modules for GUI
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtOpenGL',
        'shiboken6',
        
        # Additional Qt modules that may be needed
        'PySide6.QtDBus',
        'PySide6.QtNetwork',
        'PySide6.QtXml',
        'PySide6.QtSql',
        'PySide6.QtTest',
        
        # Standard library modules
        'ctypes',
        'threading',
        'queue',
        'tempfile',
        'xml.etree',
        'xml.etree.ElementTree',
        
        # tkinter (sometimes needed by other imports)
        'tkinter',
        'tkinter.ttk',
        'tkinter.font',
        
        # Logging
        'logging',
        'logging.handlers',
        
        # SSL/TLS for API calls
        'ssl',
        'urllib3',
        'urllib3.util',
        'urllib3.util.ssl_',
        'certifi',
        
        # HTTP libraries for API
        'http.client',
        'http.cookies',
        
        # Date/time
        'datetime',
        
        # JSON
        'json',
        
        # OS utilities
        'os.path',
        'stat',
        'fcntl',
        
        # Platform-specific
        'platform',
        'sysconfig',
        
        # Cryptography for groq
        'cryptography',
        'cryptography.hazmat',
        'cryptography.hazmat.bindings',
        'cryptography.hazmat.bindings._rust',
        
        # cffi if needed
        '_cffi_backend',
        
        # PIL/Pillow
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        'PIL.ImageFont',
        
        # For app modules
        'paste_utils',
        'display_server',
        'smart_editor',
        'transcription_store',
        'audio_buffer',
        'streaming_transcriber',
        'transcriber',
        'recorder',
        'app_context',
        'config',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'test',
        'tests',
        'pytest',
        '_pytest',
        'docs',
        'packaging',
        'setup',
        'scripts',
        'auto_start',
        'portable-start',
        '.git',
        '.github',
        'venv',
        '__pycache__',
    ],
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
    name='DictaPilot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        'vcruntime140.dll',
        'vcruntime140_1.dll',
    ],
    runtime_tmpdir=None,
    console=False,  # Set to False for GUI application (no console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(logo_path) if logo_path.exists() else None,
)