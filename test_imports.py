"""Test script to isolate the crash issue"""
import sys
print(f"Python version: {sys.version}")

print("Testing imports...")

try:
    import numpy as np
    print("✓ numpy imported successfully")
except Exception as e:
    print(f"✗ numpy failed: {e}")
    sys.exit(1)

try:
    from dotenv import load_dotenv
    print("✓ python-dotenv imported successfully")
except Exception as e:
    print(f"✗ python-dotenv failed: {e}")
    sys.exit(1)

try:
    import sounddevice as sd
    print("✓ sounddevice imported successfully")
except Exception as e:
    print(f"✗ sounddevice failed: {e}")
    sys.exit(1)

try:
    import soundfile as sf
    print("✓ soundfile imported successfully")
except Exception as e:
    print(f"✗ soundfile failed: {e}")
    sys.exit(1)

try:
    from groq import Groq
    print("✓ groq imported successfully")
except Exception as e:
    print(f"✗ groq failed: {e}")
    sys.exit(1)

print("\nTesting PySide6...")
try:
    from PySide6.QtCore import QPoint, QRectF, Qt, QTimer
    print("✓ PySide6.QtCore imported successfully")
except Exception as e:
    print(f"✗ PySide6.QtCore failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from PySide6.QtGui import QColor, QGuiApplication, QImage, QLinearGradient, QPainter, QPainterPath, QPixmap
    print("✓ PySide6.QtGui imported successfully")
except Exception as e:
    print(f"✗ PySide6.QtGui failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from PySide6.QtWidgets import QApplication, QWidget
    print("✓ PySide6.QtWidgets imported successfully")
except Exception as e:
    print(f"✗ PySide6.QtWidgets failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTesting QApplication creation...")
try:
    app = QApplication.instance() or QApplication(sys.argv[:1])
    print("✓ QApplication created successfully")
except Exception as e:
    print(f"✗ QApplication failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nAll tests passed!")
