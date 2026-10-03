#!/bin/sh
set -eu

APP_DIR="$HOME/.local/share/game-launcher"
ICON_DIR="$HOME/.local/share/icons/hicolor/256x256/apps"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"

printf '%s\n' '=== Install of Game Launcher ==='
printf '[1/6] Create the directories...\n'
mkdir -p "$APP_DIR" "$ICON_DIR" "$BIN_DIR" "$DESKTOP_DIR"

printf '[2/6] Copy of the program...\n'
cp launcher.py "$APP_DIR/launcher.py"
cp icon/game-launcher.png "$ICON_DIR/game-launcher.png"

printf '[3/6] Creating the launch command...\n'
cat > "$BIN_DIR/game-launcher" <<EOF2
#!/bin/sh
exec python3 "$APP_DIR/launcher.py" "\$@"
EOF2
chmod +x "$BIN_DIR/game-launcher"

printf '[4/6] Create the shortcut in the applications menu...\n'
cat > "$DESKTOP_DIR/game-launcher.desktop" <<EOF2
[Desktop Entry]
Name=Game Launcher
Comment=Game launcher for Wine HQ
Exec=$BIN_DIR/game-launcher
Terminal=false
Icon=$HOME/.local/share/icons/hicolor/256x256/apps/game-launcher.png
Type=Application
Categories=Game;Utility;
EOF2

printf '[5/6] Verify Python...\n'
if command -v python3 >/dev/null 2>&1; then
    printf '       Python 3 detected.\n'
else
    printf '       Warning : python3 not found.\n'
fi

printf '[6/6] Installation complete.\n'
printf '\nLaunch command : game-launcher\n'
printf 'If the command cannot be found, use : %s/game-launcher\n' "$BIN_DIR"

