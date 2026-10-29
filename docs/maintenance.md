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

`archlinux-contrib` supplies `checkservices`, which identifies system services
still using deleted executable mappings after an upgrade. Hexen offers it as a
separate post-update review with `sudo checkservices -P`; this skips `pacdiff`
and asks before each service restart. The script also reloads or re-executes
systemd when needed. See the [official package](https://archlinux.org/packages/extra/any/archlinux-contrib/)
and [upstream script](https://github.com/archlinux/contrib/blob/master/admin/checkservices).

After a system upgrade, review pacman-provided config changes before merging
them:

```sh
sudo pacdiff
```

Inspect each proposed `.pacnew`/`.pacsave` diff and choose the intended result;
these files are not safe to merge blindly. To preview package-cache cleanup
without deleting files, use `sudo paccache --dryrun --keep 3`; the weekly timer
performs the ordinary cleanup and keeps the newest three versions by default.
A recovery checkpoint's package list and `/boot` archive are separate from the
cache.

## Firewall baseline

Firewalld is the only workstation firewall manager in the base role. The role
owns `/etc/firewalld/zones/drop.xml` and uses the `drop` zone as persistent and
runtime default. Its target is `DROP`, with only the `dhcpv6-client` service
allowed; it has no ports, rich rules, or intra-zone forwarding. The packaged
zone had enabled forwarding, so Hexen replaces that definition with its
reviewed local policy. Firewalld documents that zone forwarding permits traffic
between interfaces or sources in one zone; see its official
[zone documentation](https://firewalld.org/documentation/man-pages/firewalld.zone.html).
The default drops unsolicited inbound traffic on new or unassigned
NetworkManager profiles while allowing connections initiated by the workstation
and their return traffic. Firewalld's active `allow-host-ipv6` policy retains
the ICMPv6 needed for IPv6 neighbor discovery and router advertisements. The
baseline opens no host service such as SSH.

The rehearsal VM accepted the XML, reported matching runtime and permanent
drop-zone policy, and retained DNS and IPv4 HTTPS after reload. The VM has no
IPv6 default route, so IPv6 internet behavior and inbound filtering still need
external network tests.

Check what is active before changing trust or opening a service:

```sh
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --get-default-zone
sudo firewall-cmd --list-all-zones
sudo nft list ruleset
sudo ss -lntup
```

For a focused check of the default and effective interface policy, run:

```sh
sudo firewall-cmd --get-default-zone
sudo firewall-cmd --get-active-zones
sudo firewall-cmd --zone=drop --list-all
sudo firewall-cmd --permanent --zone=drop --list-all
sudo systemctl is-enabled firewalld
sudo systemctl is-active firewalld
```

If the policy looks wrong, use a local console so a network change cannot cut
off recovery. First inspect the repository-managed policy and current state;
then restore the reviewed `ansible/roles/base/templates/firewalld-drop.xml.j2`
to `/etc/firewalld/zones/drop.xml`, set `drop` as the permanent and runtime
default, and reload firewalld:

```sh
sudo install -o root -g root -m 0644 /path/to/hexen/ansible/roles/base/templates/firewalld-drop.xml.j2 /etc/firewalld/zones/drop.xml
sudo firewall-cmd --permanent --set-default-zone=drop
sudo firewall-cmd --set-default-zone=drop
sudo firewall-cmd --reload
sudo firewall-cmd --zone=drop --list-all
```

Replace `/path/to/hexen` with the actual checkout path. The template is plain
firewalld XML and can be installed directly. Do not stop firewalld as a
recovery shortcut: that removes the host's inbound filtering. This procedure
has not yet been exercised as a recovery test.

To investigate dropped packets without enabling payload logging, inspect the
kernel journal for firewalld/nftables messages and the current firewall
counters. Do not add an unbounded logging rule as part of diagnosis:

```sh
sudo journalctl -b -u firewalld --no-pager
sudo nft list ruleset
```

The baseline does not currently install a rate-limited drop-logging rule.
Avoid logging packet payloads or forwarding firewall logs off the machine
automatically.

NetworkManager profile zones are persistent. Keep unknown/public connections in
`drop`; assign a profile to a less restrictive zone only after inspecting that
zone's services and confirming the network is trusted. For example, the stock
`home` and `work` zones can allow SSH, so do not choose them without reviewing
`firewall-cmd --info-zone home` or `--info-zone work`.

The rehearsal VM does not have LocalSend installed. Its active and permanent
`drop` zones contain no discovery ports, protocols, or rich rules, and the VM
had no UDP listeners during inspection. This verifies that the untrusted
profile has no LocalSend/discovery exception; there is no configured transfer
workflow here to test. Do not add a broad multicast or port exception without
selecting a concrete workflow and trusted NetworkManager profile.

The VM has `openvpn` and `networkmanager-openvpn` installed but no VPN profile
or provider configuration. Do not infer VPN or kill-switch behavior from the
ordinary `drop` zone; validate route and DNS behavior only after a real profile
is configured.

On 2026-10-28, a temporary TCP listener bound to all VM IPv4 addresses on port
49321. A connection attempt from the libvirt development host timed out, which
is consistent with unsolicited inbound traffic being dropped. The listener and
its temporary PID file were removed, and no listening sockets remained. This
is only a local IPv4 smoke check: it does not establish external IPv4/IPv6
filtering, a separate disposable peer, or VM forwarding behavior.

The rehearsal VM's libvirt services are disabled and its persistent `default`
network is inactive. Starting that network inside this VM would conflict with
the VM's own `192.168.122.0/24` interface subnet, so guest DHCP, DNS, NAT, and
isolation cannot be accepted in this nested setup. Podman 6.1.4 is installed
and reports rootless mode with the `netavark` backend for the desktop user, but
container connectivity and its firewall interaction have not been tested.
Those workflows need separate rehearsal tests before the firewall acceptance
checklist is complete. Firewalld manages its own nftables table; do not flush
nftables globally or disable rules owned by libvirt or containers. Review and
resolve an existing UFW or standalone nftables service configuration before
provisioning rather than running competing managers.

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
