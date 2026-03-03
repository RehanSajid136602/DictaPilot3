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
    (str(project_root / "LICENSE"), "."),
    (str(project_root / "README.md"), "."),
    (str(project_root / "docs" / "modern-ui-guide.md"), "docs"),
    (str(project_root / "dictapilot_gui" / "README.md"), "dictapilot_gui"),
    (str(project_root / "dictapilot_gui" / "requirements.txt"), "dictapilot_gui"),
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
        
        # Logging
        'logging',
        'logging.handlers',
        
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
        'secrets_manager',
        'diff_utils',
        
        # GUI modules
        'dictapilot_gui',
        'dictapilot_gui.config',
        'dictapilot_gui.config.settings',
        'dictapilot_gui.audio',
        'dictapilot_gui.audio.recorder',
        'dictapilot_gui.stt',
        'dictapilot_gui.stt.transcriber',
        'dictapilot_gui.ui',
        'dictapilot_gui.ui.main_window',
        'dictapilot_gui.ui.settings_dialog',
        
        # faster-whisper dependencies
        'faster_whisper',
        'ctranslate2',
        'tokenizers',
        'huggingface_hub',
        
        # Audio modules
        'audio.smoothing',
        'audio.vad',
        'audio.visualization_data',
        
        # Platform backends
        'x11_backend',
        'wayland_backend',
        
        # Additional dependencies that may be needed
        'dateutil',
        'dateutil.parser',
        'dateutil.tz',
        'pytz',
        'certifi',
        'idna',
        'charset_normalizer',
        'requests',
        'websockets',
        'websockets.client',
        'websockets.server',
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
        'web_ui',
        'web_server',
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

# CLI executable
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
    console=True,  # Set to True for debugging (shows console window)
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(logo_path) if logo_path.exists() else None,
)

# GUI executable (no console)
exe_gui = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DictaPilot-GUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[
        'vcruntime140.dll',
        'vcruntime140_1.dll',
    ],
    runtime_tmpdir=None,
    console=False,  # No console window for GUI
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(logo_path) if logo_path.exists() else None,
)