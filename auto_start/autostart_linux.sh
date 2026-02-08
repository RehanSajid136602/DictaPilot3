#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
AUTOSTART_DIR="$HOME/.config/autostart"
DESKTOP_FILE="$AUTOSTART_DIR/dictapilot.desktop"

if ! command -v python3 >/dev/null 2>&1; then
  echo "[ERROR] Python 3.10+ not found."
  read -r -p "Press Enter to close..."
  exit 1
fi

if [ ! -d "$ROOT_DIR/venv" ]; then
  echo "[ERROR] Virtual environment not found at: $ROOT_DIR/venv"
  echo "Run setup/setup_linux.sh first."
  read -r -p "Press Enter to close..."
  exit 1
fi

mkdir -p "$AUTOSTART_DIR"

cat > "$DESKTOP_FILE" <<DESKTOP
[Desktop Entry]
Type=Application
Version=1.0
Name=DictaPilot
Comment=Start DictaPilot at login
Terminal=false
Exec=bash -lc 'cd "$ROOT_DIR" && source venv/bin/activate && python app.py --tray'
X-GNOME-Autostart-enabled=true
DESKTOP

chmod 644 "$DESKTOP_FILE"

# Start immediately in background for one-click launch behavior.
nohup bash -lc "cd '$ROOT_DIR' && source venv/bin/activate && python app.py --tray" >/dev/null 2>&1 &

echo "[OK] Auto-start enabled: $DESKTOP_FILE"
echo "[OK] DictaPilot launched now."
read -r -p "Press Enter to close..."
