# Game Launcher

A simple GTK3 launcher for Linux/Windows games via Wine.

# Copyright (C) 2026

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

## Install

```bash
sudo apt update
sudo apt install python3 python3-gi gir1.2-gtk-3.0
cd game-launcher
chmod +x install.sh
./install.sh
```

## Launch

```bash
game-launcher
```

The data is saved in `~/.config/game-launcher/games.json`
