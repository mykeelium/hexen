#!/bin/bash

set -ouex pipefail

### Install packages

# Packages can be installed from any enabled yum repo on the image.
# RPMfusion repos are available by default in ublue main images
# List of rpmfusion packages can be found here:
# https://mirrors.rpmfusion.org/mirrorlist?path=free/fedora/updates/43/x86_64/repoview/index.html&protocol=https&redirect=1
dnf5 install -y btop 
dnf5 install -y clang
dnf5 install -y fzf # cli fuzzy find
dnf5 install -y git
dnf5 install -y libfido2
dnf5 install -y neovim python3-neovim
dnf5 install -y ripgrep

# might need to use terrapkg - see: https://github.com/terrapkg/packages/tree/frawhide
# dnf5 install -y zed

# flatpak?
# dnf5 install -y obsidian


# COPR

# Enable and Install
dnf5 -y copr enable scottames/ghostty
dnf5 install -y ghostty

dnf5 -y copr enable dejan/lazygit
dnf5 install -y lazygit

# dnf5 -y copr enable sneexy/zen-browser
# dnf5 install -y zen-browser

dnf5 -y copr enable varlad/zellij
dnf5 install -y zellij

# Disable
dnf5 -y copr disable scottames/ghostty
dnf5 -y copr disable dejan/lazygit
# dnf5 -y copr disable sneexy/zen-browser
dnf5 -y copr disable varlad/zellij

#### Example for enabling a System Unit File

systemctl enable podman.socket

# Configuration

# neovim
mkdir -p /tmp/
git clone https://github.com/mykeelium/nvim-config.git /tmp/nvim-config
mv -r /tmp/nvim-config/pack /usr/share/nvim
mkdir -p /etc/skel/.config
ln -s /usr/share/nvim /etc/skel/.config/nvim
NVIM_APPNAME=nvim \
XDG_DATA_HOME=/usr/share \
XDG_STATE_HOME=/var/lib/nvim \
nvim --headless "+Lazy! sync" +qa
chmod -R 755 /usr/share/nvim
chmod -R 755 /usr/share/nvim/site



rm -rf /tmp/*
