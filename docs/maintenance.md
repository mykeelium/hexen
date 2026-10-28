# Workstation maintenance baseline

The base Ansible role installs and configures these maintenance tools. This page
describes the intended operating rules; VM and physical-machine acceptance
remains tracked in `operations-roadmap.md`.

## Package cache and configuration changes

`pacman-contrib` supplies `pacdiff` and `paccache`. The enabled weekly
`paccache.timer` uses the package default and keeps the newest three cached
versions per package. This leaves several downgrade candidates while bounding
cache growth. The package cache lives on its own Btrfs subvolume, so it is not
included in root snapshots.

After a system upgrade, review pacman-provided config changes before merging
them:

```sh
sudo pacdiff
```

Inspect each proposed `.pacnew`/`.pacsave` diff and choose the intended result;
these files are not safe to merge blindly. To preview package-cache cleanup
without deleting files, use `sudo paccache --dryrun --remove`; the weekly timer
performs the ordinary cleanup. A recovery checkpoint's package list and `/boot`
archive are separate from the cache.

## Firewall baseline

Firewalld is the only workstation firewall manager in the base role. It starts
at boot with the `drop` zone as the persistent and runtime default. This drops
unsolicited inbound traffic on new or unassigned NetworkManager profiles while
allowing connections initiated by the workstation and their return traffic.
Firewalld's built-in `allow-host-ipv6` policy retains the ICMPv6 needed to bring
up IPv6. The baseline opens no host service such as SSH.

Check what is active before changing trust or opening a service:

```sh
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --get-default-zone
sudo firewall-cmd --list-all-zones
sudo nft list ruleset
sudo ss -lntup
```

NetworkManager profile zones are persistent. Keep unknown/public connections in
`drop`; assign a profile to a less restrictive zone only after inspecting that
zone's services and confirming the network is trusted. For example, the stock
`home` and `work` zones can allow SSH, so do not choose them without reviewing
`firewall-cmd --info-zone home` or `--info-zone work`.

This first baseline does not yet configure LocalSend, Windows/libvirt, Podman,
or VPN exceptions. Those workflows need separate rehearsal tests before the
firewall acceptance checklist is complete. Firewalld manages its own nftables
table; do not flush nftables globally or disable rules owned by libvirt or
containers. Review and resolve an existing UFW or standalone nftables service
configuration before provisioning rather than running competing managers.

## Backups and hardware maintenance

`restic` is installed as a tool only. It creates no repository or schedule
until an off-device destination, encryption secret, exclusions, and recovery
method have been selected. Keep secrets out of Git and make them independently
recoverable. Test restoring files and a quiesced VM image to a separate path
before relying on a backup.

`fwupd` and `smartmontools` are installed for explicit maintenance checks.
Inspect firmware support with `fwupdmgr get-devices` and available updates with
`fwupdmgr get-updates`; installing firmware and rebooting remain deliberate
owner actions. Inspect drive support and health with `sudo smartctl --scan-open`
and the device-specific `sudo smartctl -a /dev/DEVICE` command. Virtual disks
cannot establish physical firmware or SMART compatibility.

`power-profiles-daemon` starts at boot. Available profiles depend on firmware
and hardware; inspect with `powerprofilesctl list` and select with
`powerprofilesctl set PROFILE`. Validate thermals, battery behavior, and
suspend/resume on the physical laptop. Do not enable another power-management
service until its ownership is reconciled with this daemon.
