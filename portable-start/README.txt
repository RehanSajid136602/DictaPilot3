DictaPilot One-Click Start Scripts
===================================

This folder contains portable one-click start scripts for DictaPilot that can be copied
to any location on your computer. Simply double-click the appropriate script for your
operating system to launch the app.

REQUIREMENTS
------------
Before using these scripts, ensure you have:
1. Python 3.10 or higher installed
2. Run the appropriate setup script for your OS:
   - Windows: setup\setup_windows.bat
   - Linux: setup/setup_linux.sh
   - macOS: setup/setup_macos.command

This will create the virtual environment and install all required dependencies.

USAGE
-----
Choose the script for your operating system:

Windows:
  Double-click: start_windows.bat

Linux:
  Double-click: start_linux.sh
  (Make sure the file is executable: chmod +x start_linux.sh)

macOS:
  Double-click: start_macos.command

PORTABILITY
-----------
These scripts are designed to be portable. You can copy this entire folder to any
location on your computer (Desktop, Documents, Downloads, etc.) and they will work
as long as the folder structure is maintained:

  Your Location/
  └── portable-start/
      ├── start_windows.bat
      ├── start_linux.sh
      ├── start_macos.command
      └── README.txt

The scripts automatically detect their location and find the project root directory.

TROUBLESHOOTING
---------------
If you encounter errors:

1. "Python 3.10+ not found"
   - Install Python from https://www.python.org/downloads/
   - Make sure to add Python to your system PATH

2. "Virtual environment not found"
   - Run the setup script for your OS first
   - Ensure the venv folder exists in the project root

3. "app.py not found"
   - Ensure this portable-start folder is in the correct location
   - It should be a subfolder of the DictaPilot project directory

4. Script won't run on Linux/macOS
   - Make the script executable: chmod +x start_linux.sh or chmod +x start_macos.command
   - On macOS, you may need to allow the script in Security & Privacy settings

For more information, visit the DictaPilot project repository.
