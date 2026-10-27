# VM investigation: 2026-10-25

This is an evidence record. Archinstall completed successfully and the first
disk boot reached the LUKS passphrase prompt. Boot through to the installed
login, provisioning repeatability, updates, and recovery remain unverified.

## Confirmed in the running VM

- VM: `hexen-archinstall`, QEMU/KVM through `qemu:///system`.
- UEFI firmware; Secure Boot disabled in the VM definition.
- Four CPUs, 8 GiB RAM, one blank 64 GiB writable disk, plus a read-only ISO.
- Live ISO `/version`: `2026.10.01`.
- Packages: `archinstall 4.5-1`, `mkinitcpio 42.1-1`,
  `qemu-guest-agent 11.1.1-4`.
- The live shell is accessible through SPICE.
- QEMU guest-agent commands work, including adding the dedicated public SSH key.
- SSH login succeeds with the host's `~/.ssh/hexen-vm` key and strict checking
  against a host public key independently retrieved through the guest agent.
- Archinstall's menu runs over an SSH pseudo-terminal in dry-run/offline mode.
  Its bootloader choices include Limine; its Limine submenu exposes unified
  kernel images, removable-location installation, and Plymouth.
- The menu investigation was exited without completing a configuration export
  or performing an installation.

### Follow-up: shared dry-run walkthrough

After network recovery, a new dry-run was started in the live guest's tmux
session `hexen-install`. Menu input and text captures confirmed these settings:

| Choice | Dry-run value |
| --- | --- |
| Target preview | The single 64 GiB Virtio disk; no disk operations performed |
| Partition layout | 1 GiB FAT32 ESP at `/boot`; remaining space for Btrfs |
| Btrfs | `compress=zstd`; `@`, `@home`, `@log`, `@pkg` |
| Snapshot integration | None selected in the installer |
| Bootloader | Limine, UKI disabled, removable-location installation disabled |
| Profile | Minimal; no graphics driver or greeter selected |
| Networking | NetworkManager default backend (`type: nm`) |
| Kernel | `linux` |
| Swap | zram enabled, zstd |
| Locale | US keyboard, `en_US.UTF-8`, UTF-8, default console font |
| VM hostname | `hexen-vm` |
| Timezone | `America/New_York` |
| NTP | Enabled |
| Additional packages | None selected yet |

A preliminary **non-credential** export was inspected only inside the VM and
renamed to `/root/hexen-research/preliminary-unencrypted-do-not-install.json`.
It contains this VM's device selection and does not yet include encryption or
authentication. It must not be used as an install profile or checked into the
repository.

Within the encryption submenu, LUKS was selected and the Btrfs system partition
was marked for encryption; the ESP was not offered as an encryption target.
The owner entered the encryption passphrase and created `mcuomo` with sudo
access. The resulting menu and non-secret export confirmed LUKS applies only
to the Btrfs partition. The disk remained blank throughout the dry-run.

### Follow-up: real installer ready for final confirmation

The completed dry-run exported its configuration and credentials into
`/run/hexen-install` in the live VM. The directory is mode `0700`; both exports
were restricted to `0600`. Credential contents were not displayed or copied
to the host/repository. Selecting Install in **dry-run mode** completed validation
and exited without modifying the disk.

A VM-only runtime configuration, `/run/hexen-install/actual-vm-config.json`, was
prepared from that checked export with these explicit development additions:

- Official-repository packages: `git`, `openssh`, and `qemu-guest-agent`.
- Enabled services: `sshd.service` and `qemu-guest-agent.service`.
- A post-install command installs only the dedicated public key into
  `/home/mcuomo/.ssh/authorized_keys`, sets directory/file modes `0700`/`0600`,
  and assigns them to the user's primary group and ownership. No private key
  is copied into the guest.

The command runs inside Archinstall's target chroot, after user creation.
These are development-VM additions, not changes to the shared workstation
package/service declarations. The custom command contains a public key only;
passwords remain in the separate root-only runtime credential file.

The real installer was started interactively in tmux session `hexen-install`
with `--config` and `--creds` pointing at those VM-local runtime files, without
`--silent`. It reached the final configuration confirmation. The reloaded
non-secret configuration still identifies `/dev/vda`, LUKS on the Btrfs
partition, Limine with UKI/removable disabled, and the two VM support services.
`lsblk` still showed a blank disk at that point. The owner then gave the final
interactive confirmation and reported that installation had started.

### Follow-up: completed installation and first disk boot

Archinstall reported successful completion in 48 seconds. Before rebooting,
inspection of the mounted installation confirmed:

- `/dev/vda1`: 1 GiB FAT ESP mounted at `/boot`.
- `/dev/vda2`: LUKS header version 2, opened as `/dev/mapper/root`.
- Btrfs inside the encrypted mapping, with root `@`, home `@home`, logs `@log`,
  and package cache `@pkg`, all mounted as planned.
- Installed `linux 7.2.11.arch1-1`, `limine 12.9.4-1`, and
  `mkinitcpio 42.2-1`.
- `/boot/EFI/arch-limine/limine.conf` references the ordinary Linux kernel and
  initramfs on the ESP. Its command line identifies LUKS by PARTUUID, opens
  mapper `root`, mounts `subvol=@`, and disables zswap for the zram setup.
- mkinitcpio uses `udev` and `encrypt`, with keyboard/keymap support. Inspection
  of the initramfs file list found `hooks/encrypt` and `usr/bin/cryptsetup`,
  with no matching embedded key-file paths in the checked names.
- The firmware entry points to `EFI/arch-limine/BOOTX64.EFI`, and the
  installer-created `99-limine.hook` redeploys EFI binaries to that same
  directory after Limine package updates.
- Kernel, initramfs, and the x86_64 EFI binary exist on the ESP.
- NetworkManager and SSH are enabled. The QEMU guest agent is activated by
  the installed virtio-port udev rule; its unit is static, which is expected.
- `mcuomo` is UID/GID 1000 and belongs to `wheel`. SSH directory/key permissions
  are `0700`/`0600`, owned by `mcuomo:mcuomo`.

The installed SSH host keys were generated in the target chroot, and only the
public Ed25519 host key was saved on the host for strict verification after
boot. No credential export existed in the installed Archinstall log directory.
The runtime credential export was removed before shutdown. The target
filesystems were unmounted and the encrypted mapping closed cleanly.

The VM's persistent definition already had disk-only boot order and an empty
virtual CD-ROM. After a clean power-off and start, a console inspection showed
the installed initramfs asking for the passphrase for `/dev/vda2`. The owner
has been asked to unlock it. Boot to login and post-boot SSH checks are pending.

## Networking: initial failure and verified recovery

The guest interface `enp1s0` had carrier and an IPv6 link-local address, but no
IPv4 DHCP lease. The default libvirt network is active and declares DHCP on
`192.168.122.0/24`; a dnsmasq process exists. Renewing DHCP did not obtain a lease.

For diagnosis only, after an ARP duplicate-address probe received no responses,
the live guest was assigned `192.168.122.250/24` with a default route through
`192.168.122.1`. This is temporary and **not** a reserved address or a reusable
installation setting. The address is inside the DHCP pool, so it must not be
adopted as a permanent static configuration without changing the allocation plan.

With that temporary address:

- SSH from the host succeeds.
- ICMP to the host gateway and `1.1.1.1` succeeds.
- A DNS lookup with temporary per-link DNS `1.1.1.1` did not return an address.
- TCP connection attempts to gateway DNS (`192.168.122.1:53`), public DNS
  (`1.1.1.1:53`), and public HTTPS (`1.1.1.1:443`) timed out. ICMP success is
  therefore insufficient evidence of working Internet access.
- Time synchronization reported `NTPSynchronized=no`.

Internet package installation is not yet verified. Temporary addresses, routes,
DNS settings, and live-ISO SSH authorization disappear on reboot.

### Follow-up: host firewall diagnosis

The owner supplied privileged dnsmasq logs and the complete nftables ruleset.
dnsmasq is listening on `virbr0` with the expected DHCP range. The ruleset shows:

- UFW's input policy drops DHCP requests (28 packets hit the UDP destination
  port 67 drop-policy rule), and has no bridge DNS allow rules.
- UFW's forwarding policy is drop, with an empty `ufw-user-forward` chain.
- Libvirt's own forwarding and NAT rules exist in `ip libvirt_network`.
- Docker/UFW integration returns private-source traffic to the normal chains;
  it does not supply an outbound allow rule for this VM network.

Together these account for the observed DHCP, DNS, and new TCP connection
failures. The host route lookup confirms `wlan0` is the current uplink. Four
scoped UFW rules were prepared and accepted by the installed UFW command parser:
bridge DHCP, bridge UDP/TCP DNS, and subnet egress from `virbr0` through `wlan0`.
See the [host-rule instructions](../vm/README.md#ufw-with-libvirts-nftables-backend).

The owner applied those rules using FIDO-backed sudo. The agent did not change
host firewall rules or services. The guest then acquired DHCP address
`192.168.122.237/24`.

After verifying the DHCP route, the temporary `192.168.122.250` address, manually
added default route, and per-link public DNS override were removed. Live-ISO
networking was restarted through the guest agent to avoid losing the control
channel during address changes. Verification afterward showed:

- Only the DHCP IPv4 address remains on `enp1s0`.
- The default route uses `192.168.122.1` with `proto dhcp`.
- DNS is supplied by the gateway `192.168.122.1`; `archlinux.org` resolves.
- `curl --head https://archlinux.org/` returns HTTP 200.
- `NTPSynchronized=yes`.
- SSH works at the DHCP address with strict host-key checking.

This confirms network recovery, not package installation or encrypted disk boot.

The live ISO subsequently completed `pacman -Sy --noconfirm`: `core` was current
and `extra` downloaded successfully. Package metadata queries found `linux`,
`mkinitcpio`, and `openssh` in `core`, and `limine` and `qemu-guest-agent` in
`extra`. This verifies repository metadata access and those package channels;
it does not prove successful package archive installation or boot. SSH and
guest-agent support for the installed development VM must be configured
explicitly before leaving the live ISO; neither service is an implicit
requirement for the eventual work laptop.

## Findings from the installed Archinstall 4.5 source

These were read from the package in the VM, not inferred from current online
documentation. They predict installer behavior; they do not replace boot tests.

| Area | Implementation finding | Repository implication |
| --- | --- | --- |
| Dry-run | `scripts/guided.py` returns before filesystem operations when `dry_run` is set, after configuration saving and layout validation | Suitable for menu research; exported credentials still need protection |
| Default ESP | `lib/disk/default_layouts.py` proposes a 1 GiB FAT32 partition mounted at `/boot` | Matches the planned non-UKI boot layout; verify final summary |
| Default Btrfs subvolumes | `@` at `/`, `@home` at `/home`, `@log` at `/var/log`, and `@pkg` at `/var/cache/pacman/pkg` | Default list has no separate `/.snapshots` mount; choosing automatic snapshot integration is a separate action |
| Limine validation | `lib/bootloader/utils.py` validates FAT boot storage and rejects an ESP outside `/boot` in the single-ESP, non-UKI layout | Keep `/boot` as ESP mountpoint for the initial path |
| Passphrase-only encryption | `lib/installer.py` prepares `encrypt` and converts systemd hooks to udev/keymap when no HSM is selected | The live ISO's own systemd-based mkinitcpio configuration does not establish the installed system's hooks |
| Mapper naming | Passphrase-only root parameters use mapper name `root`; they may identify LUKS by PARTUUID | Do not assume the repo's `cryptroot` name is the installed mapping |
| Limine custom location | Non-removable UEFI installation writes the EFI binaries and `limine.conf` under `EFI/arch-limine/` | Differs from the role's `EFI/limine/` and top-level `limine.conf` |
| Limine removable location | Removable installation writes its binaries and configuration under `EFI/BOOT/` | Record this choice explicitly before deciding which files Ansible owns |
| Limine updates | Installer writes `/etc/pacman.d/hooks/99-limine.hook` to redeploy its selected EFI binaries after a Limine package transaction | Existing instructions about manual deployment describe the manual fallback, not this installer-managed path |

The relevant Limine implementation is `Installer._add_limine_bootloader`.
Encryption hooks and parameters are in `Installer._prepare_encrypt`,
`Installer.mkinitcpio`, and `Installer._get_kernel_params_partition`.

## Next acceptance steps

1. DHCP, DNS, HTTPS to Arch's site, and time synchronization are verified.
   Package download and installation still need their own verification.
2. The dry-run choice record and credential entry are complete: Limine, ordinary
   kernel/initramfs, Btrfs default subvolumes, passphrase-only encryption, zram,
   NetworkManager, and Minimal. UKI, removable-location installation, and
   Plymouth are disabled.
3. Keep actual disk selection and credentials interactive, then verify the
   final summary against the disposable VM before installing.
4. Boot the installed system and inspect its real hooks, mapper, mountpoints,
   Limine files, firmware entry, and package hook.
5. Reconcile the Ansible boot role with that proven path before running it.
6. Test update/reboot, repeat provisioning, and root snapshot recovery.
