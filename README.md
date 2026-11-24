# Game Launcher

A launcher with a simple graphical interface that lets you organize your Windows and Linux games into a graphical library and launch them using the corresponding Wine configuration. Includes a “Wine Tools” menu that provides quick access to several Wine tools.

Supported systems :
- Debian 11 / 12 / 13
- Ubuntu 22.04 / 24.04 / 26.04

## Install

Check dependencies
```bash
sudo apt update
sudo apt install python3 python3-gi gir1.2-gtk-3.0
```

From the installation folder
```bash
cd game-launcher
chmod +x install.sh
./install.sh
```

## Launch

```bash
game-launcher
```

The data is stored in `~/.config/game-launcher/games.json`


## Copyright (C) 2026

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
