#!/bin/sh
set -eu

APP_DIR="$HOME/.local/share/game-launcher"
BIN_FILE="$HOME/.local/bin/game-launcher"
DESKTOP_FILE="$HOME/.local/share/applications/game-launcher.desktop"
ICON_FILE="$HOME/.local/share/icons/hicolor/256x256/apps/game-launcher.png"
CONFIG_DIR="$HOME/.config/game-launcher"

printf '%s\n' '=== Uninstalling Game Launcher ==='
printf '[1/3] Removing the launcher...\n'
rm -f "$BIN_FILE"

printf '[2/3] Deleting application files...\n'
rm -rf "$APP_DIR"
rm -f "$DESKTOP_FILE"
rm -f "$ICON_FILE"

printf '[3/3] User data...\n'
if [ -d "$CONFIG_DIR" ]; then
    printf 'Also delete the configured user games shortcuts ? [y/N] '
    read answer
    case "$answer" in
        y|Y|yes|Yes|YES)
            rm -rf "$CONFIG_DIR"
            printf '       User data deleted.\n'
            ;;
        *)
            printf '       User data preserved in %s\n' "$CONFIG_DIR"
            ;;
    esac
fi

printf '%s\n' 'Uninstallation complete.'
