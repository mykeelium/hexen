#!/bin/bash

set -ouex pipefail
mkdir -p /tmp/

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
dnf5 install -y golang

# might need to use terrapkg - see: https://github.com/terrapkg/packages/tree/frawhide
# dnf5 install -y zed

# flatpak?
# dnf5 install -y obsidian


# gopls
GOBIN=/usr/bin GOMODCACHE=/tmp/go-mod HOME=/tmp go install golang.org/x/tools/gopls@latest
# go packages
mkdir -p /usr/share/go/pkg/mod-cache
pushd /tmp
cat > go.mod << 'GOMOD'
module preload

go 1.25

require (
    github.com/gorilla/handlers v1.5.2
    github.com/gorilla/mux v1.8.1
    github.com/gorilla/schema v1.4.1
    github.com/go-chi/chi/v5 v5.1.0
    github.com/labstack/echo/v4 v4.12.0
    gorm.io/gorm v1.25.12
    gorm.io/driver/postgres v1.5.9
    gorm.io/driver/sqlite v1.5.6
    github.com/lib/pq v1.10.9
    github.com/pkg/errors v0.9.1
    github.com/redis/go-redis/v9 v9.7.0
    github.com/spf13/viper v1.19.0
    github.com/spf13/cobra v1.8.1
    github.com/sirupsen/logrus v1.9.3
    github.com/golang-jwt/jwt/v5 v5.2.1
    golang.org/x/crypto v0.47.0
    golang.org/x/mod v0.32.0
    golang.org/x/oauth2 v0.32.0
    golang.org/x/text v0.33.0
    golang.org/x/tools v0.41.0
    go.uber.org/mock v0.5.2
    gotest.tools v2.2.0+incompatible
)
GOMOD

GOMODCACHE=/usr/share/go/pkg/mod-cache HOME=/tmp go mod download -x
popd
chmod -R 755 /usr/share/go

# add pachage cache so users have access
cat > /etc/profile.d/go-env.sh << 'EOF'
# Use system-wide Go module cache as fallback
if [ ! -d "$HOME/go/pkg/mod" ] && [ -d "/usr/share/go/pkg/mod-cache" ]; then
  mkdir -p "$HOME/go/pkg"
  cp -r /usr/share/go/pkg/mod-cache "$HOME/go/pkg/mod"
fi
EOF
chmod 644 /etc/profile.d/go-env.sh

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

# TODO: remove if neovim packaing works
# package.path = "/usr/share/nvim/config/?.lua;/usr/share/nvim/config/lua/?.lua;/usr/share/nvim/config/lua/?/init.lua;" .. package.path

# neovim
mkdir -p /usr/share/nvim
mkdir -p /usr/share/nvim/lazy
mkdir -p /usr/share/nvim/plugins
mkdir -p /var/lib/nvim/lazy

git clone --filter=blob:none --branch=stable https://github.com/folke/lazy.nvim.git /usr/share/nvim/lazy
git clone https://github.com/mykeelium/nvim-config.git /tmp/nvim-config
cp -a /tmp/nvim-config/pack/. /usr/share/nvim/

# Create symlink for user skeleton
mkdir -p /etc/skel/.config
ln -s /usr/share/nvim /etc/skel/.config/nvim

NVIM_APPNAME=nvim \
HOME=/var/lib/nvim \
XDG_CONFIG_HOME=/usr/share \
XDG_DATA_HOME=/usr/share \
XDG_CACHE_HOME=/var/lib/nvim \
XDG_STATE_HOME=/var/lib/nvim \
nvim --headless "+Lazy! restore" +qa

chmod -R 755 /usr/share/nvim 
chmod -R 755 /var/lib/nvim



rm -rf /tmp/*
