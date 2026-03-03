"""
DictaPilot GUI - Main Entry Point
Run with: python -m dictapilot_gui
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from PySide6.QtWidgets import QApplication
    from PySide6.QtCore import Qt
    from dictapilot_gui.ui.main_window import MainWindow
except ImportError as e:
    print(f"Error: Required package not found: {e}")
    print("\nPlease install dependencies:")
    print("  pip install -r requirements.txt")
    sys.exit(1)


def main():
    """Main entry point"""
    # Enable high DPI scaling
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("DictaPilot")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("DictaPilot")
    
    # Set application-wide font
    font = app.font()
    font.setPointSize(10)
    app.setFont(font)
    
    # Create and show main window
    window = MainWindow()
    window.show()
    
    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()