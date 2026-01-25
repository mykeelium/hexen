#!/bin/bash
set -ouex pipefail

# Enable Hyprland COPR
dnf5 -y copr enable solopasha/hyprland

# Install Hyprland and core dependencies
dnf5 install -y \
    hyprland \
    hyprpaper \
    hyprlock \
    hypridle \
    hyprsunset \
    hyprpicker \
    xdg-desktop-portal-hyprland

# Disable COPR after install
dnf5 -y copr disable solopasha/hyprland

# Install status bar and launcher
dnf5 install -y \
    waybar \
    wofi

# Install notification daemon
dnf5 install -y mako

# Install clipboard tools (wl-clipboard should be pre-installed)
dnf5 install -y wl-clipboard || true

# Install cliphist from COPR (clipboard history)
dnf5 -y copr enable atim/starship
dnf5 install -y cliphist || echo "cliphist not available, clipboard history disabled"
dnf5 -y copr disable atim/starship || true

# SwayOSD - try to install, skip if not available
dnf5 install -y SwayOSD || echo "SwayOSD not available, using alternative volume controls"

# Install screenshot tool
dnf5 install -y \
    grim \
    slurp

# Check if hyprshot is available, otherwise we'll use grim+slurp
dnf5 install -y hyprshot || echo "hyprshot not available, using grim+slurp"

# Install utilities (most are pre-installed in sway-atomic)
dnf5 install -y --skip-unavailable \
    playerctl \
    brightnessctl \
    blueman \
    pavucontrol \
    network-manager-applet \
    nautilus \
    jq

# Try to install polkit authentication agent
dnf5 install -y lxpolkit || dnf5 install -y polkit-kde-agent-1 || echo "Polkit agent: using system default"

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
