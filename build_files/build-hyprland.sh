#!/bin/bash
set -ouex pipefail

# =============================================================================
# Hyprland 0.53+ Build Script for Fedora
# =============================================================================
# Optimized with parallel compilation and build caching.
# Builds everything from source to ensure compatibility.
# =============================================================================

# -----------------------------------------------------------------------------
# Configuration
# -----------------------------------------------------------------------------
BUILD_DIR="/var/hypr-build"
PIDS=()
FAILED=0

# -----------------------------------------------------------------------------
# Helper Functions
# -----------------------------------------------------------------------------

# Run a command in the background and track its PID
run_parallel() {
    "$@" &
    PIDS+=($!)
}

# Wait for all parallel jobs and fail if any failed
wait_all() {
    local failed=0
    for pid in "${PIDS[@]}"; do
        if ! wait "$pid"; then
            failed=1
        fi
    done
    PIDS=()
    if [ "$failed" -ne 0 ]; then
        echo "ERROR: One or more parallel builds failed"
        exit 1
    fi
}

# Clone or update a git repository (enables incremental builds with caching)
git_clone_or_update() {
    local repo_url="$1"
    local dir_name="$2"
    local branch="${3:-}"
    local depth="${4:---depth 1}"

    if [ -d "$dir_name/.git" ]; then
        echo "Updating existing clone: $dir_name"
        cd "$dir_name"
        git fetch --all
        if [ -n "$branch" ]; then
            git checkout "$branch"
            git reset --hard "origin/$branch" 2>/dev/null || git reset --hard "$branch"
        else
            git reset --hard origin/HEAD 2>/dev/null || git pull
        fi
        cd "$BUILD_DIR"
    else
        echo "Fresh clone: $dir_name"
        rm -rf "$dir_name"
        if [ -n "$branch" ]; then
            git clone $depth --branch "$branch" "$repo_url" "$dir_name"
        else
            git clone $depth "$repo_url" "$dir_name"
        fi
    fi
}

# Build a cmake project
build_cmake_project() {
    local name="$1"
    local extra_args="${2:-}"

    echo "Building $name..."
    cd "$BUILD_DIR/$name"
    rm -rf build
    cmake -B build -G Ninja \
        -DCMAKE_BUILD_TYPE=Release \
        -DCMAKE_INSTALL_PREFIX=/usr \
        $extra_args
    ninja -C build
    ninja -C build install
    echo "Completed $name"
    cd "$BUILD_DIR"
}

# Build a meson project
build_meson_project() {
    local name="$1"
    local extra_args="${2:-}"

    echo "Building $name..."
    cd "$BUILD_DIR/$name"
    rm -rf _build
    meson setup _build . --prefix=/usr --wrap-mode=nodownload $extra_args
    ninja -C _build
    ninja -C _build install
    echo "Completed $name"
    cd "$BUILD_DIR"
}

# -----------------------------------------------------------------------------
# Install build dependencies
# -----------------------------------------------------------------------------
# Note: xdg-desktop-portal-hyprland is built from source below
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
    libinput-devel \
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
    xcb-util-errors-devel \
    pugixml-devel \
    libseat-devel \
    libzip-devel \
    libuuid-devel \
    libXcursor-devel \
    re2-devel \
    muParser-devel \
    iniparser-devel \
    pipewire-devel \
    qt6-qtbase-devel \
    qt6-qtwayland-devel \
    xdg-desktop-portal

# -----------------------------------------------------------------------------
# Setup build directory
# -----------------------------------------------------------------------------
mkdir -p "$BUILD_DIR"
mkdir -p /usr/share/wayland-sessions/
cd "$BUILD_DIR"

# =============================================================================
# PHASE 0: No dependencies (can run in parallel)
# - wayland-protocols
# - glaze
# =============================================================================
echo "=== PHASE 0: Building base dependencies ==="

git_clone_or_update "https://gitlab.freedesktop.org/wayland/wayland-protocols.git" "wayland-protocols" "" ""
git_clone_or_update "https://github.com/stephenberry/glaze.git" "glaze" "v6.1.0" "--depth 1"

run_parallel build_meson_project "wayland-protocols"
run_parallel build_cmake_project "glaze" "-Dglaze_ENABLE_FUZZING=OFF -Dglaze_BUILD_TESTS=OFF -DBUILD_TESTING=OFF"
wait_all

pkg-config --modversion wayland-protocols

# =============================================================================
# PHASE 1: Depends only on wayland-protocols (can run in parallel)
# - hyprwayland-scanner
# - hyprutils
# =============================================================================
echo "=== PHASE 1: Building hyprwayland-scanner and hyprutils ==="

git_clone_or_update "https://github.com/hyprwm/hyprwayland-scanner.git" "hyprwayland-scanner"
git_clone_or_update "https://github.com/hyprwm/hyprutils.git" "hyprutils"

run_parallel build_cmake_project "hyprwayland-scanner"
run_parallel build_cmake_project "hyprutils"
wait_all

# =============================================================================
# PHASE 2: Depends on hyprutils (can run in parallel)
# - hyprlang
# - hyprgraphics
# - hyprwire
# =============================================================================
echo "=== PHASE 2: Building hyprlang, hyprgraphics, hyprwire ==="

git_clone_or_update "https://github.com/hyprwm/hyprlang.git" "hyprlang"
git_clone_or_update "https://github.com/hyprwm/hyprgraphics.git" "hyprgraphics"
git_clone_or_update "https://github.com/hyprwm/hyprwire.git" "hyprwire"

run_parallel build_cmake_project "hyprlang"
run_parallel build_cmake_project "hyprgraphics"
run_parallel build_cmake_project "hyprwire"
wait_all

# =============================================================================
# PHASE 3: Depends on hyprlang (can run in parallel)
# - hyprcursor
# - aquamarine
# =============================================================================
echo "=== PHASE 3: Building hyprcursor and aquamarine ==="

git_clone_or_update "https://github.com/hyprwm/hyprcursor.git" "hyprcursor"
git_clone_or_update "https://github.com/hyprwm/aquamarine.git" "aquamarine" "" ""

run_parallel build_cmake_project "hyprcursor"
run_parallel build_cmake_project "aquamarine"
wait_all

# Update library cache before building Hyprland
ldconfig

# =============================================================================
# PHASE 4: Hyprland (sequential - needs all above)
# =============================================================================
echo "=== PHASE 4: Building Hyprland ==="

# Hyprland needs full clone for submodules
if [ -d "Hyprland/.git" ]; then
    echo "Updating existing Hyprland clone"
    cd Hyprland
    git fetch --all
    git reset --hard origin/main
    git submodule update --init --recursive
    cd "$BUILD_DIR"
else
    rm -rf Hyprland
    git clone --recursive https://github.com/hyprwm/Hyprland
fi

cd "$BUILD_DIR/Hyprland"
rm -rf build
cmake -S . -B build -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
ninja -C build
ninja -C build install
cd "$BUILD_DIR"

# =============================================================================
# PHASE 5: Depends on Hyprland (can run in parallel)
# - hyprland-protocols
# - hyprtoolkit
# =============================================================================
echo "=== PHASE 5: Building hyprland-protocols and hyprtoolkit ==="

git_clone_or_update "https://github.com/hyprwm/hyprland-protocols.git" "hyprland-protocols"
git_clone_or_update "https://github.com/hyprwm/hyprtoolkit.git" "hyprtoolkit"

run_parallel build_cmake_project "hyprland-protocols"
run_parallel build_cmake_project "hyprtoolkit"
wait_all

# Update library cache
ldconfig

# =============================================================================
# PHASE 6: Hyprland utilities (can all run in parallel)
# - hyprpaper
# - hypridle
# - hyprlock
# - hyprsunset
# - hyprpicker
# - xdg-desktop-portal-hyprland
# - hyprland-guiutils
# =============================================================================
echo "=== PHASE 6: Building Hyprland utilities ==="

git_clone_or_update "https://github.com/hyprwm/hyprpaper.git" "hyprpaper"
git_clone_or_update "https://github.com/hyprwm/hypridle.git" "hypridle"
git_clone_or_update "https://github.com/hyprwm/hyprlock.git" "hyprlock"
git_clone_or_update "https://github.com/hyprwm/hyprsunset.git" "hyprsunset"
git_clone_or_update "https://github.com/hyprwm/hyprpicker.git" "hyprpicker"
git_clone_or_update "https://github.com/hyprwm/xdg-desktop-portal-hyprland.git" "xdg-desktop-portal-hyprland"
git_clone_or_update "https://github.com/hyprwm/hyprland-guiutils.git" "hyprland-guiutils"

run_parallel build_cmake_project "hyprpaper"
run_parallel build_cmake_project "hypridle"
run_parallel build_cmake_project "hyprlock"
run_parallel build_cmake_project "hyprsunset"
run_parallel build_cmake_project "hyprpicker"
run_parallel build_cmake_project "xdg-desktop-portal-hyprland"
run_parallel build_cmake_project "hyprland-guiutils"
wait_all

echo "=== All Hyprland components built successfully ==="

# -----------------------------------------------------------------------------
# Cleanup build-only dependencies (but keep build dir for caching)
# -----------------------------------------------------------------------------
cd /

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
cp -r /ctx/config/wofi /etc/skel/.config/

# Set correct permissions
chmod -R 755 /etc/skel/.config/hypr
chmod -R 755 /etc/skel/.config/waybar
chmod -R 755 /etc/skel/.config/mako
chmod -R 755 /etc/skel/.config/wofi
