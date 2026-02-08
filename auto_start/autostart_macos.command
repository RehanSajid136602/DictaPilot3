#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
LAUNCH_AGENTS_DIR="$HOME/Library/LaunchAgents"
PLIST_PATH="$LAUNCH_AGENTS_DIR/com.dictapilot.app.plist"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERROR] Python 3.10+ not found."
  read -r -p "Press Enter to close..."
  exit 1
fi

if [ ! -d "$ROOT_DIR/venv" ]; then
  echo "[ERROR] Virtual environment not found at: $ROOT_DIR/venv"
  echo "Run setup/setup_macos.command first."
  read -r -p "Press Enter to close..."
  exit 1
fi

mkdir -p "$LAUNCH_AGENTS_DIR"

cat > "$PLIST_PATH" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.dictapilot.app</string>

  <key>ProgramArguments</key>
  <array>
    <string>/bin/bash</string>
    <string>-lc</string>
    <string>cd "$ROOT_DIR" &amp;&amp; source venv/bin/activate &amp;&amp; exec python app.py --tray</string>
  </array>

  <key>RunAtLoad</key>
  <true/>

  <key>KeepAlive</key>
  <false/>

  <key>StandardOutPath</key>
  <string>/tmp/dictapilot.out.log</string>

  <key>StandardErrorPath</key>
  <string>/tmp/dictapilot.err.log</string>
</dict>
</plist>
PLIST

launchctl unload "$PLIST_PATH" >/dev/null 2>&1 || true
launchctl load "$PLIST_PATH"
launchctl kickstart -k "gui/$(id -u)/com.dictapilot.app" >/dev/null 2>&1 || true

echo "[OK] Auto-start enabled: $PLIST_PATH"
echo "[OK] DictaPilot launched now."
read -r -p "Press Enter to close..."
