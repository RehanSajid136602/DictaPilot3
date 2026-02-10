DictaPilot Portable Start Scripts
=================================

These scripts let you start DictaPilot by double-clicking, after setup is complete.

FILES
-----
- `start_windows.bat`
- `start_linux.sh`
- `start_macos.command`

HOW THEY WORK
-------------
Each script:
1. Detects the script location
2. Treats the parent directory as project root
3. Verifies Python, `venv`, and `app.py`
4. Activates `venv`
5. Runs `python app.py`

REQUIREMENTS
------------
Before using these scripts:
1. Install Python 3.10+
2. Run one setup script once:
   - Windows: `setup\setup_windows.bat`
   - Linux: `./setup/setup_linux.sh`
   - macOS: `./setup/setup_macos.command`
3. Add `GROQ_API_KEY` in `.env`

USAGE
-----
Windows:
- Double-click `start_windows.bat`

Linux:
- Make executable once: `chmod +x start_linux.sh`
- Double-click or run `./start_linux.sh`

macOS:
- Double-click `start_macos.command`
- If blocked by Gatekeeper, allow it in Privacy & Security, then run again

IMPORTANT FOLDER LAYOUT
-----------------------
Do not move these files out of the repo structure. They expect:

  DictaPilot/
  ├── app.py
  ├── venv/
  └── portable-start/
      ├── start_windows.bat
      ├── start_linux.sh
      ├── start_macos.command
      └── README.txt

TROUBLESHOOTING
---------------
1. Python not found:
   - Install from https://www.python.org/downloads/

2. Virtual environment missing:
   - Run setup script for your OS
   - Confirm `venv` exists in project root

3. `app.py` not found:
   - Confirm `portable-start` is inside the DictaPilot repo

4. Linux/macOS script does not launch:
   - Run `chmod +x start_linux.sh start_macos.command`

See also:
- Root guide: `README.md`
- Quick setup: `QUICK_START.txt`
