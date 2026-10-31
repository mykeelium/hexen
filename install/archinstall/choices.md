# Archinstall walkthrough and machine choices

This is the menu-by-menu guide for Hexen's base installation. Archinstall installs
Arch, encryption, and Limine first; `install/provision.sh` adds the Hexen desktop
and applications after the installed system boots.

Menu labels below were checked against **Archinstall 4.5** on the official
**2026.10.01 ISO**, including the menu source installed in the rehearsal VM.
The partition layout also matches the previous successful VM installation.
This is a human-readable choice record, not an exported installer configuration.
If another installer version shows different prompts, stop and check those
prompts rather than guessing from their position in the menu.

## Machine choices

Use the **rehearsal VM** column for the current walkthrough. The earlier
`hexen-archinstall` VM is a separate recovery-tested installation; leave it alone.

| Setting | Rehearsal VM | Future work laptop |
| --- | --- | --- |
| Libvirt VM name | `hexen-rehearsal-20261027` | Not applicable |
| Installed hostname | `hexen-rehearsal` | Choose after identifying the machine; `numen`/`arcana` profiles are not implemented yet |
| Install target | New, blank 64 GiB Virtio disk, currently `/dev/vda` | Pending hardware inventory and independent backup; never copy the VM device name |
| Firmware | UEFI; Secure Boot disabled | Verify firmware and Secure Boot requirements before installing |
| Partition layout | GPT; 1 GiB FAT32 ESP at `/boot`; remaining space encrypted with LUKS2 and containing Btrfs | Same intended layout, pending hardware acceptance |
| Btrfs subvolumes | `@`, `@home`, `@log`, `@pkg`; compression enabled | Same intended layout |
| LVM / installer snapshots | Both unset | Both unset for the current supported layout |
| Bootloader | Limine; UKI off; removable location off; Plymouth off | Same initial contract; firmware exceptions need separate review |
| Kernel / swap | `linux`; zram with `zstd`; no disk swap | Same initial choices |
| User | `mcuomo`, with sudo access; root password unset | Same if this remains the owner's account name |
| Keyboard / locale | `us`; `en_US.UTF-8`; `UTF-8`; default console font | Same unless the physical keyboard needs another layout |
| Timezone / NTP | `America/New_York`; NTP enabled | Same unless the owner chooses otherwise |
| Network | Network Manager, default backend; virtual Ethernet via DHCP | Network Manager; configure actual Wi-Fi after installation |
| Profile | Minimal; no installer desktop or greeter | Same; Hexen provisions the desktop later |
| Additional packages | `git`, `ansible`, `openssh`, `qemu-guest-agent` | `git`, `ansible`; remote access is a separate decision |

No passwords, private keys, disk UUIDs, or account recovery data belong in this
file. The VM disk path on the **host** is
`/var/lib/libvirt/images/hexen-rehearsal-20261027.qcow2`; inside the **guest** it
appears as `/dev/vda`. These are two names for the same disposable virtual disk.

## 1. Open the installer

In the rehearsal VM's graphical console, the existing installer is in tmux:

```sh
tmux attach -t hexen-install
```

Do not run a second installer if that session is already running. For a new
installation without that prepared session, run `archinstall` at the live ISO
shell instead. This walkthrough is for the real installer, not `--dry-run`.

The main menu starts with **Archinstall language**, **Locales**, and
**Mirrors and repositories**. It ends with **Save configuration**, **Install**,
and **Abort**. Changing menu choices prepares a plan; final Install confirmation
is the point that authorizes disk changes.

Navigation:

- Use **Up/Down** to highlight an entry and **Enter** to open or accept it.
- In a list that allows several selections, **Space** toggles the highlighted
  entry. A highlighted row is not necessarily selected. Check its selection mark,
  then press **Enter** to accept the selected set.
- Use **/** to search/filter when the screen offers it. In package selection,
  clear the filter before searching for the next package; previous selections
  stay selected.
- In a submenu, select **← Back** to retain its choices and return. It may be
  below the visible rows; scroll down.
- **Esc** cancels/skips the current prompt where allowed; it can retain the
  previous value. It is not a reliable way to clear a setting.
- **Ctrl+C** is Reset on these menus, not the normal Back key. **Ctrl+Q** quits.
  Use the footer or **F1** if you are unsure which keys a screen supports.

## 2. Language and locale

1. Main menu → **Archinstall language** → **English**.
2. Main menu → **Locales**:
   - **Keyboard layout** → **us**.
   - **Locale language** → **en_US.UTF-8**.
   - **Locale encoding** → **UTF-8**.
   - **Console font** → leave the existing default/unset value.
3. Select **← Back**.

Keyboard layout controls which characters your physical keys produce, including
when entering the disk passphrase. Locale controls language and formatting;
it is a separate setting.

## 3. Package mirrors

1. Main menu → **Mirrors and repositories**.
2. **Select regions** → mark **United States** with Space → Enter.
3. Leave **Add custom servers**, **Optional repositories**, and
   **Add custom repository** unset/empty.
4. Select **← Back**.

Mirrors are download servers for the official packages. This install does not
need testing, multilib, or a third-party package repository. If the mirror list
cannot load, resolve networking before continuing.

## 4. Partition the disposable disk

This choice will erase the selected disk when installation is confirmed.
For this rehearsal, select only the new blank 64 GiB Virtio disk. If it is not
clearly identifiable, stop. Do not select a disk based only on its device name.

1. Main menu → **Disk configuration** → **Partitioning**.
2. Select **Use a best-effort default partition layout**.
3. At **Select disks for the installation**, highlight the blank 64 GiB disk
   (`/dev/vda` in this VM), press **Space** to mark it, then **Enter**.
4. At **Select main filesystem**, select **btrfs**.
5. At **Would you like to use BTRFS subvolumes with a default structure?**,
   select **Yes**.
6. At **Would you like to use compression or disable CoW?**, select
   **Use compression**. Do not select **Disable Copy-on-Write**.
7. You return to **Disk configuration**. Leave **LVM** unset.

There is no separate GPT or ESP-sizing prompt in this default UEFI path.
The generated layout should have a **1 GiB FAT32 `/boot`** partition and a
Btrfs partition occupying the rest. Inspect the Partitioning preview. Its Btrfs
subvolume table should show:

| Subvolume | Mountpoint | Purpose |
| --- | --- | --- |
| `@` | `/` | Installed OS and system configuration |
| `@home` | `/home` | Personal files, outside root snapshot rollback |
| `@log` | `/var/log` | Logs, outside root snapshot rollback |
| `@pkg` | `/var/cache/pacman/pkg` | Downloaded package cache |

These are separate filesystem trees sharing the Btrfs space, rather than four
fixed-size disk partitions. With the default subvolumes selected, a separate
`/home` partition question should not appear. If it does, revisit the subvolume
choice before continuing.

## 5. Encrypt the system partition

Still inside **Disk configuration**:

1. Open **Disk encryption**.
2. **Encryption type** → **LUKS**. Do not choose either LVM variant.
3. **Encryption password** → enter and confirm your disk-unlock passphrase.
   Enter it yourself; do not paste it into chat or save it in this repository.
4. **Iteration time** → retain the default **10000 ms**. This is the password
   derivation cost, not a countdown you need to configure elsewhere.
5. **Partitions** → mark the large **Btrfs system partition**, then Enter.
   The FAT32 ESP must remain unencrypted; the selector excludes boot partitions.
   The system partition may be described by its planned size/filesystem rather
   than an existing `/dev/vda2` name because it has not been created yet.
6. Leave **HSM** unset. It is optional hardware-token disk unlocking, not the
   ordinary passphrase setup. **LVM volumes** is not applicable to this layout.
7. Select **← Back** to return to **Disk configuration**.
8. Leave **Btrfs snapshots** unset. Do not choose Snapper or Timeshift here;
   Hexen's Ansible role initializes Snapper later. If you already chose an
   installer snapshot tool, use that selector's Reset action to clear it and
   check that its preview is empty.
9. Inspect **Disk encryption**: expect **LUKS**, a configured hidden password,
   and **1 selected partition**. Selecting LUKS alone does not select a partition.
10. Select **← Back** to return to the main menu.

The ESP contains the files needed before the encrypted OS can unlock. Both root
and home live inside the encrypted Btrfs partition. Root snapshots still do not
back up home data.

## 6. Swap and bootloader

1. Main menu → **Swap**.
2. **Would you like to use swap on zram?** → **Yes**.
3. **Select zram compression algorithm:** → **zstd**.

Zram is compressed RAM used as swap. This path does not create disk swap or
configure hibernation.

4. Main menu → **Bootloader**. This opens a submenu:
   - **Bootloader** → **Limine**.
   - **Unified kernel images** → **No** (disabled).
   - **Install to removable location** → **No** (disabled).
   - **Plymouth** → leave unset/disabled. If you open it, answer **No** to
     **Would you like to enable it?**
5. Select **← Back**.

The top-level Bootloader entry and its nested Bootloader entry are different
screens. UKI combines boot components into one EFI image; Hexen currently
validates the separate kernel/initramfs path. Removable location controls the
EFI file path, not whether the VM disk itself is removable. This rehearsal uses
Limine's custom location and a firmware boot entry, even though the installer
recommends the removable path as a general default. Plymouth is a cosmetic boot
splash; leave the passphrase prompt visible for acceptance testing.

If Plymouth was already enabled, its theme selector supports Reset to clear it;
check its preview afterward. Pressing Esc alone retains the previous value.

## 7. Kernel, firmware, and hostname

1. Main menu → **Kernels** → ensure only **linux** is marked → Enter.
   Do not add linux-lts, linux-zen, or linux-hardened for this rehearsal.
2. **Additional firmware** → leave the optional list empty for this VM.
   This is extra firmware beyond the installer's standard firmware selection;
   it does not mean omit all firmware. Physical hardware needs its own review.
3. **Hostname** → enter **hexen-rehearsal** → Enter.

The hostname is the installed machine's network name. It need not match the
libvirt VM name.

## 8. Create the administrative account

1. Main menu → **Authentication**.
2. Leave **Root password** unset. Use the regular account with sudo instead.
3. **User account** → **Add a user**.
4. At **Enter a username**, enter **mcuomo**.
5. Enter and confirm the account password yourself.
6. At **Should "mcuomo" be a superuser (sudo)?**, select **Yes**.
7. In the user list, select **Confirm and exit**. Verify the account is listed
   with sudo enabled. If necessary, highlight the existing user and use
   **Promote/Demote user** to correct that choice; do not create a duplicate.
8. Leave **U2F login setup** unset for the VM. Hardware-key login/sudo is separate
   from creating this basic account and from the disk-unlock **HSM** option.
9. Select **← Back**.

The disk passphrase unlocks storage at boot. The account password logs you in
and authorizes sudo. They are separate credentials with separate prompts.

## 9. Base profile and applications

1. Main menu → **Profile** → **Type** → **Minimal**.
2. Leave **Graphics driver** and **Greeter** unset if shown; they may be disabled
   for Minimal. Select **← Back**.
3. Main menu → **Applications** → leave all entries unset:
   **Bluetooth**, **Audio**, **Print service**, **Power management**,
   **Firewall**, and **Additional fonts**. Select **← Back**.

Minimal means Archinstall supplies the base OS. Do not choose Desktop/Hyprland
here: Hexen installs its reviewed desktop and services through Ansible later.
Unset installer application options do not mean those features are excluded
from Hexen's later provisioning.

## 10. Network and package manager

1. Main menu → **Network configuration** →
   **Use Network Manager (default backend)**.
2. Do not select **Copy ISO network configuration to installation**, the iwd
   backend, standalone iwd, or Manual configuration for this rehearsal.
3. Main menu → **Pacman** → leave **Parallel Downloads** and **Color** at their
   existing defaults → **← Back**.

The network selection controls the installed OS. The live ISO already has its
own working network. Virtual Ethernet should use DHCP after boot; do not copy
its current IP address into a static configuration.

## 11. Bootstrap packages, timezone, and clock

1. Main menu → **Additional packages**. Wait for the package list to load.
2. Search for each exact package name with **/** and mark it with **Space**:
   - **git** — clone the actual repository after first boot.
   - **ansible** — run the provisioner.
   - **openssh** — VM remote access support.
   - **qemu-guest-agent** — VM inspection and management through libvirt.
3. Clear the search between package names. Press **Enter** after marking all
   four. Check the preview contains those exact packages, not similarly named
   packages or a whole package group.
4. Main menu → **Timezone** → search/select **America/New_York**.
5. **Automatic time sync (NTP)** → **Yes**.

The last two packages are development-VM choices. Installing OpenSSH does not
by itself set up authorized keys or guarantee that SSH is enabled. Arrange access
explicitly after installation; no private host key should be copied into the VM.

## 12. Review before Install

You can leave **Save configuration** alone. A saved export is not required to
install, and may contain secrets or device-specific identifiers. Do not check an
export into Git; this document is the persistent machine-choice record.

Before selecting **Install**, review the previews for these exact results:

- Only the new rehearsal disk is selected: blank 64 GiB Virtio `/dev/vda`.
- Planned wipe applies only to that disposable VM disk.
- A 1 GiB FAT32 ESP at `/boot`, plus the remaining space for Btrfs.
- Btrfs compression and `@`, `@home`, `@log`, `@pkg` mountpoints as listed above.
- LUKS encryption on the Btrfs partition; a passphrase is configured; ESP excluded.
- LVM and installer Btrfs snapshot integration unset; no disk swap.
- Limine; UKI disabled; removable location disabled; Plymouth unset.
- Only `linux`; Minimal profile; no greeter or installer application extras.
- `mcuomo` with sudo; root password and U2F setup unset.
- Hostname `hexen-rehearsal`; US locale/keyboard; New York timezone; NTP on.
- Network Manager default backend and the four explicit bootstrap packages.

Select **Install**, read the final summary, and confirm only if it matches.
If something differs, return to the relevant menu and correct it first. Keep
disk selection, passwords, and final destructive confirmation interactive.

## 13. Finish installation and boot the disk

1. Wait for **Installation completed**. If installation reports an error, stop;
   do not treat a partial installation as ready to reboot.
2. At **What would you like to do next?**, choose **Exit archinstall** so the
   result can be inspected before reboot. A chroot is not needed for the normal
   path; any VM access preparation is a separate explicit step.
3. Power off the live VM with `poweroff` at its shell.
4. In virt-manager, open this VM's hardware details, select the virtual CD-ROM,
   and disconnect/eject its ISO. In **Boot Options**, ensure the virtual disk is
   enabled for boot. Keep the disk attached. Start the VM again.
5. Confirm you boot the installed **Limine** entry, receive the **LUKS passphrase**
   prompt, and reach the login prompt. Log in as **mcuomo**.

Do not choose automatic reboot before arranging disk boot: otherwise the VM can
boot the ISO again. Reaching `root@archiso` means you are still in the installer.

## 14. Verify and provision after first disk boot

Run inside the installed VM:

```sh
lsblk -f
findmnt /
findmnt /home
findmnt /boot
swapon --show
sudo systemctl --failed --no-pager
```

Expect encrypted Btrfs root at `@`, distinct home at `@home`, FAT ESP at `/boot`,
and only zram swap. Find the actual LUKS partition in `lsblk` and inspect it with
`sudo cryptsetup luksDump /dev/ACTUAL_LUKS_PARTITION`; its header must report
**Version: 2**. Do not guess a partition name on another machine.

Clone as the regular user, not root, into its permanent location. If `~/hexen`
already exists, inspect it instead of overwriting it:

```sh
git clone https://github.com/mykeelium/hexen.git "$HOME/hexen"
cd "$HOME/hexen"
git log -1 --oneline
./install/provision.sh --vm
```

The `--vm` flag leaves nested libvirt networks unmanaged to avoid a subnet
collision with the VM uplink. Keep this flag on repeat runs of this rehearsal.
Use the plain workstation command on the laptop once its hardware is accepted.

Confirm this checkout is the reviewed revision intended for the rehearsal;
uncommitted/unpushed host changes are not included in a GitHub clone. Record the
actual commit with acceptance evidence. Follow the provisioner's prompts and
enter sudo authorization yourself.

At **Desktop launcher [walker/fuzzel]**, press Enter to select the default,
**walker**, after following [`../manual-apps/walker/README.md`](../manual-apps/walker/README.md)
to review and install its pinned manual packages. If those packages are not
installed, provisioning stops with instructions. Choose **fuzzel** only if you
want the optional launcher from signed Arch packages instead. See
[`../manual-apps/README.md`](../manual-apps/README.md) for the separate vendor
applications; the provisioner does not install them.

After successful provisioning, rerun the same command with the same launcher
choice and confirm Ansible reports zero changes and no failures. Follow
[`../../docs/desktop.md`](../../docs/desktop.md) for starting the desktop and
acceptance, and [`../../docs/recovery.md`](../../docs/recovery.md) before update
or rollback tests. Completing these menu choices alone does not complete those
acceptance gates.

## References and scope of verification

- [Archinstall guided installation](https://archinstall.archlinux.page/installing/guided.html)
  for the overall interactive workflow. Online examples can describe a different
  release; the installed 4.5 menu source supplied the labels above.
- [Previous installation evidence](observations-2026-10-25.md) for the successful
  encrypted Btrfs/Limine layout and first boot.
- [VM development workflow](../vm/README.md) for consoles and explicit remote access.

The rehearsal VM's menus/source, blank disk, UEFI, DNS, HTTPS, and time sync were
checked on 2026-10-27. The owner completed installation from the official
2026.10.01 ISO using Archinstall 4.5, then confirmed Limine boot, LUKS unlock,
and login to `mcuomo`. Initial `./install/provision.sh --vm` completed at source
revision `d2a4f8d` with Fuzzel selected; the remaining clean-VM application and
current-source acceptance gates are tracked in `docs/operations-roadmap.md`.
Laptop disk identity, graphics, firmware, Wi-Fi, input, and suspend behavior
remain unvalidated; do not treat the VM-specific choices as a laptop inventory.
