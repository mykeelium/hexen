#!/bin/bash
set -ouex pipefail

# Ensure keyring starts for COSMIC sessions via systemd user service
cat > /etc/systemd/user/gnome-keyring-daemon.service << 'EOF'
[Unit]
Description=GNOME Keyring (secrets)
PartOf=graphical-session.target
After=graphical-session.target

[Service]
Type=simple
ExecStart=/usr/bin/gnome-keyring-daemon --foreground --components=secrets
Restart=on-failure

[Install]
WantedBy=graphical-session.target
EOF

mkdir -p /etc/systemd/user/graphical-session.target.wants
ln -sfn /etc/systemd/user/gnome-keyring-daemon.service /etc/systemd/user/graphical-session.target.wants/gnome-keyring-daemon.service
