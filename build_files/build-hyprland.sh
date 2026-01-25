#!/bin/bash
set -ouex pipefail

# Install hyprland specific dependencies
dnf5 install -y hyperland hyprpaper hyperlock hyperidle waybar wofi make

# mkdir -p /etc/skel/.config
# cp -r ../config/hypr /etc/skel/.config/
# cp -r ../config/waybar /etc/skel/.config/
# cp -r ../config/mako /etc/skel/.config/
