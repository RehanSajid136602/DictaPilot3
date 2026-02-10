DictaPilot Auto-Start Scripts
=============================

These scripts register DictaPilot to launch at login and also start it immediately.

FILES
-----
- `autostart_windows.bat`
- `autostart_linux.sh`
- `autostart_macos.command`

PREREQUISITES
-------------
1. Python 3.10+ installed
2. Setup already completed (`venv` exists):
   - Windows: `setup\setup_windows.bat`
   - Linux: `./setup/setup_linux.sh`
   - macOS: `./setup/setup_macos.command`
3. `.env` contains `GROQ_API_KEY`

USAGE
-----
Windows:
- Double-click `autostart_windows.bat`
- It creates: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\DictaPilot_Start.bat`

Linux:
- Make executable once: `chmod +x autostart_linux.sh`
- Run: `./autostart_linux.sh`
- It creates: `~/.config/autostart/dictapilot.desktop`

macOS:
- Double-click `autostart_macos.command`
- It creates: `~/Library/LaunchAgents/com.dictapilot.app.plist`

NOTES
-----
- These scripts launch `python app.py --tray`.
- They do not remove existing setup files; you can rerun them safely.

DISABLE AUTO-START
------------------
Windows:
- Delete `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\DictaPilot_Start.bat`

Linux:
- Delete `~/.config/autostart/dictapilot.desktop`

macOS:
- Run:
  `launchctl unload ~/Library/LaunchAgents/com.dictapilot.app.plist`
- Then delete:
  `~/Library/LaunchAgents/com.dictapilot.app.plist`

TROUBLESHOOTING
---------------
1. `venv` missing:
   - Run setup script first.

2. No startup on next login:
   - Re-run script and confirm startup file was created.

3. App starts but cannot paste/hotkey:
   - Recheck OS accessibility/input permissions.

See also:
- Root guide: `README.md`
- One-click scripts: `portable-start/README.txt`
