#!/bin/bash
set -ouex pipefail

# =============================================================================
# Hyprland 0.53+ Build Script for Fedora
# =============================================================================
# Uses ashbuk COPR for Hyprland core (0.53.1+) and builds utilities from source
# to ensure compatibility with the new window rule syntax.
# =============================================================================

# -----------------------------------------------------------------------------
# Install Hyprland core from ashbuk COPR (has 0.53.1+)
# -----------------------------------------------------------------------------
dnf5 -y copr enable ashbuk/Hyprland-Fedora

dnf5 install -y \
    xdg-desktop-portal-hyprland

dnf5 -y copr disable ashbuk/Hyprland-Fedora

# packages I might be coming back to
# wayland-protocols-devel \

# -----------------------------------------------------------------------------
# Install build dependencies
# -----------------------------------------------------------------------------
dnf5 install -y \
    cmake \
    ninja-build \
    gcc-c++ \
    git \
    meson \
    wayland-devel \
    cairo-devel \
    pango-devel \
    libdrm-devel \
    mesa-libgbm-devel \
    mesa-libEGL-devel \
    libxkbcommon-devel \
    libjpeg-turbo-devel \
    libwebp-devel \
    file-devel \
    pam-devel \
    sdbus-cpp-devel \
    systemd-devel \
    pixman-devel \
    libglvnd-devel \
    hwdata-devel \
    libdisplay-info-devel \
    tomlplusplus-devel \
    zip \
    librsvg2-devel \
    libX11-devel \
    pixman-devel \
    libxcb-devel \
    xcb-util-devel \
    xcb-util-image-devel \
    xcb-util-renderutil-devel \
    xcb-util-wm-devel \
    pugixml-devel \
    libseat-devel \
    libzip-devel \
    libuuid-devel \
    libXcursor-devel \
    re2-devel \
    muParser-devel

# Create build directory
BUILD_DIR="/tmp/hypr-build"
mkdir -p "$BUILD_DIR"
mkdir -p /usr/share/wayland-sessions/
cd "$BUILD_DIR"

# build hyprland from source

# build wayland-protocols
git clone https://gitlab.freedesktop.org/wayland/wayland-protocols.git
cd wayland-protocols
meson setup _build . --prefix=/usr --wrap-mode=nodownload
ninja -C _build
ninja -C _build install
cd "$BUILD_DIR"

pkg-config --modversion wayland-protocols

# -----------------------------------------------------------------------------
# Build hyprwayland-scanner (needed for building hypr tools)
# -----------------------------------------------------------------------------
git clone --depth 1 https://github.com/hyprwm/hyprwayland-scanner.git
cd hyprwayland-scanner
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
ninja -C build
ninja -C build install
cd "$BUILD_DIR"

# -----------------------------------------------------------------------------
# Build hyprutils (utility library)
# -----------------------------------------------------------------------------
git clone --depth 1 https://github.com/hyprwm/hyprutils.git
cd hyprutils
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
ninja -C build
ninja -C build install
cd "$BUILD_DIR"

# -----------------------------------------------------------------------------
# Build hyprlang (config language library)
# -----------------------------------------------------------------------------
git clone --depth 1 https://github.com/hyprwm/hyprlang.git
cd hyprlang
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
ninja -C build
ninja -C build install
cd "$BUILD_DIR"

# -----------------------------------------------------------------------------
# Build hyprcursor (cursor library) - MUST be before Hyprland
# -----------------------------------------------------------------------------
git clone --depth 1 https://github.com/hyprwm/hyprcursor.git
cd hyprcursor
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
ninja -C build
ninja -C build install
cd "$BUILD_DIR"

# -----------------------------------------------------------------------------
# Build hyprgraphics (graphics library) - MUST be before Hyprland
# -----------------------------------------------------------------------------
git clone --depth 1 https://github.com/hyprwm/hyprgraphics.git
cd hyprgraphics
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
ninja -C build
ninja -C build install
cd "$BUILD_DIR"

# -----------------------------------------------------------------------------
# Build aquamarine (backend library)
# -----------------------------------------------------------------------------
git clone https://github.com/hyprwm/aquamarine.git
cd aquamarine
cmake -S . -B build -G Ninja \
  -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX=/usr
ninja -C build
ninja -C build install
cd "$BUILD_DIR"

# -----------------------------------------------------------------------------
# Build hyprwire (IPC library) - MUST be before Hyprland
# -----------------------------------------------------------------------------
git clone --depth 1 https://github.com/hyprwm/hyprwire.git
cd hyprwire
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
ninja -C build
ninja -C build install
cd "$BUILD_DIR"

# Update library cache before building Hyprland
ldconfig

# -----------------------------------------------------------------------------
# Build Hyprland (requires: hyprcursor, hyprgraphics, aquamarine, hyprlang, hyprutils, hyprwire)
# -----------------------------------------------------------------------------
git clone --recursive https://github.com/hyprwm/Hyprland
cd Hyprland
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
ninja -C build
ninja -C build install
cd "$BUILD_DIR"

# -----------------------------------------------------------------------------
# Build and install hyprpaper (wallpaper utility)
# -----------------------------------------------------------------------------
git clone --depth 1 https://github.com/hyprwm/hyprpaper.git
cd hyprpaper
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
ninja -C build
ninja -C build install
cd "$BUILD_DIR"

# -----------------------------------------------------------------------------
# Build and install hypridle (idle daemon)
# -----------------------------------------------------------------------------
git clone --depth 1 https://github.com/hyprwm/hypridle.git
cd hypridle
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
ninja -C build
ninja -C build install
cd "$BUILD_DIR"

# -----------------------------------------------------------------------------
# Build and install hyprlock (screen locker)
# -----------------------------------------------------------------------------
git clone --depth 1 https://github.com/hyprwm/hyprlock.git
cd hyprlock
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
ninja -C build
ninja -C build install
cd "$BUILD_DIR"

# -----------------------------------------------------------------------------
# Build and install hyprsunset (blue light filter)
# -----------------------------------------------------------------------------
git clone --depth 1 https://github.com/hyprwm/hyprsunset.git
cd hyprsunset
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
ninja -C build
ninja -C build install
cd "$BUILD_DIR"

# -----------------------------------------------------------------------------
# Build and install hyprpicker (color picker)
# -----------------------------------------------------------------------------
git clone --depth 1 https://github.com/hyprwm/hyprpicker.git
cd hyprpicker
cmake -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
ninja -C build
ninja -C build install
cd "$BUILD_DIR"

# -----------------------------------------------------------------------------
# Cleanup build directory and build-only dependencies
# -----------------------------------------------------------------------------
cd /
rm -rf "$BUILD_DIR"

# Remove build-only packages to reduce image size
dnf5 remove -y \
    cmake \
    ninja-build \
    gcc-c++ \
    git \
    meson \
    || true

# Clean dnf cache
dnf5 clean all

# -----------------------------------------------------------------------------
# Install other Hyprland ecosystem tools from repos
# -----------------------------------------------------------------------------

# Install status bar and launcher
dnf5 install -y \
    waybar \
    wofi

# Install notification daemon
dnf5 install -y mako

# Install clipboard tools
dnf5 install -y wl-clipboard || true

# Install cliphist from COPR (clipboard history)
dnf5 -y copr enable atim/starship
dnf5 install -y cliphist || echo "cliphist not available, clipboard history disabled"
dnf5 -y copr disable atim/starship || true

# SwayOSD - try to install, skip if not available
dnf5 install -y SwayOSD || echo "SwayOSD not available, using alternative volume controls"

# Install screenshot tools
dnf5 install -y \
    grim \
    slurp

# Check if hyprshot is available
dnf5 install -y hyprshot || echo "hyprshot not available, using grim+slurp"

# Install utilities
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

# -----------------------------------------------------------------------------
# Copy Hyprland configuration to skeleton
# -----------------------------------------------------------------------------
mkdir -p /etc/skel/.config
cp -r /ctx/config/hypr /etc/skel/.config/
cp -r /ctx/config/waybar /etc/skel/.config/
cp -r /ctx/config/mako /etc/skel/.config/

# Set correct permissions
chmod -R 755 /etc/skel/.config/hypr
chmod -R 755 /etc/skel/.config/waybar
chmod -R 755 /etc/skel/.config/mako
