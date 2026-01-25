#!/bin/bash
set -ouex pipefail

# Install Hyprland and core dependencies
dnf5 install -y \
    hyprland \
    hyprpaper \
    hyprlock \
    hypridle \
    hyprsunset \
    hyprpicker \
    xdg-desktop-portal-hyprland

# Install status bar and launcher
dnf5 install -y \
    waybar \
    wofi

# Install notification daemon
dnf5 install -y mako

# Install OSD and clipboard tools
dnf5 install -y \
    swayosd \
    wl-clipboard \
    cliphist

# Install screenshot tool
dnf5 install -y \
    grim \
    slurp

# Check if hyprshot is available, otherwise we'll use grim+slurp
dnf5 install -y hyprshot || echo "hyprshot not available, using grim+slurp"

# Install utilities
dnf5 install -y \
    playerctl \
    brightnessctl \
    blueman \
    pavucontrol \
    network-manager-applet \
    polkit-gnome \
    nautilus \
    jq

# Install fonts
dnf5 install -y \
    jetbrains-mono-fonts-all \
    fontawesome-fonts-all

# Copy Hyprland configuration to skeleton
mkdir -p /etc/skel/.config
cp -r /ctx/config/hypr /etc/skel/.config/
cp -r /ctx/config/waybar /etc/skel/.config/
cp -r /ctx/config/mako /etc/skel/.config/

# Set correct permissions
chmod -R 755 /etc/skel/.config/hypr
chmod -R 755 /etc/skel/.config/waybar
chmod -R 755 /etc/skel/.config/mako
