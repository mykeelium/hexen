# Guided Archinstall procedure

This procedure intentionally keeps destructive disk selection and all credentials interactive. A saved Archinstall disk configuration can point at a stale device name or omit the intended encryption settings; do not replay one blindly.

For exact menu paths, nested prompts, and the saved rehearsal-VM choices, follow
the [Archinstall walkthrough and machine choices](choices.md). It covers every
top-level menu in Archinstall 4.5, the final review, and first-boot provisioning.

## Experimental generated configuration

The new generator prepares the documented single-disk configuration and shows
it before launching Archinstall. It currently targets **Archinstall 4.5 only**,
on the official x86_64 Arch ISO booted in UEFI mode. Installation acceptance
with this generator is still pending; use a new disposable VM disk for rehearsal.
Existing partitions, partition tables, filesystems, mounted devices, read-only
devices, and disks smaller than 40 GiB are refused.

From the live ISO, connect to the internet, download this repository archive (the live ISO need not have Git), and run:

```sh
curl -fL --retry 3 -o /tmp/hexen-source.tar.gz https://github.com/mykeelium/hexen/archive/refs/heads/main.tar.gz
bsdtar -xf /tmp/hexen-source.tar.gz
cd hexen-main
./install/archinstall/hexen-install.sh
```

This previews the plan without partitioning. It asks for a disk, hostname,
username, timezone, keyboard layout, locale, and mirror country code. Review the
plain-language summary; add `--json` to inspect the generated JSON. To launch the experimental install on a disposable disk, rerun:

```sh
./install/archinstall/hexen-install.sh --install
```

The install path requires typing `ERASE` followed by the selected device path.
Passwords are entered with hidden prompts during the in-memory handoff; a
credentials file is not generated. Archinstall then opens its normal review
menu. Check **Disk configuration → Disk encryption**, **Authentication**, the
bootloader, and the entire final summary before selecting **Install**. Leave
**Save credentials** alone: explicitly saving credentials in Archinstall can
persist the disk passphrase. The adapter rechecks disk identity and LUKS
configuration immediately before Archinstall performs disk operations.

The temporary non-secret config is removed on exit. Archinstall can retain its
own non-secret configuration and logs. An aborted menu is not reported as a
successful installation. No reboot or post-install provisioning is automatic.
Follow the boot checks below, then run `./install/first-boot.sh --vm` as the new
regular account in the VM. It installs prerequisites, guides Walker setup, and
runs provisioning. The generated base config
installs Git and Ansible; it does not configure SSH or remote access.

## Run the guided installer

1. Boot the official Arch installation ISO in UEFI mode.
2. Run `lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,MODEL` and identify the blank virtual disk by size/model.
3. Start the installer with `archinstall`.
4. Follow [`choices.md`](choices.md), selecting the target disk interactively and configuring UEFI/GPT, an unencrypted EFI System Partition, LUKS2 encryption, and Btrfs for the system volume.
5. Select Limine if the current installer offers it. Archinstall 4.5 installed Limine 12.9.4 successfully for the documented encrypted Btrfs layout in the disposable VM. Recheck the installer version and final summary on each installation; if Limine is unavailable or the layout differs, stop and review the manual Limine procedure in `../limine/README.md` before proceeding.
6. Enter the LUKS passphrase and user credentials at the prompts. Do not save an Archinstall `user_credentials.json` file in this repository. Archinstall's upstream docs distinguish general configuration from credentials because encryption passwords are sensitive.
7. Review the final summary carefully. The only target must be the disposable VM disk; verify the encryption and filesystem choices. Only then confirm the install.

Archinstall configuration names and menus change over time. The VM test confirms the observed Archinstall 4.5/Limine 12.9.4 combination, not every future installer version. Use the current [guided installation documentation](https://archinstall.archlinux.page/installing/guided.html) and the options presented by the ISO rather than copying a stale JSON example. Before confirming, record the selected EFI mountpoint, Btrfs root and home subvolumes, any `/.snapshots` mount, and the encryption and bootloader choices.

## Verify after first boot

At the Limine menu, boot the installed system. Confirm it prompts for the LUKS passphrase and reaches the login prompt. Then inspect the block devices:

```sh
lsblk -f
```

Find the LUKS partition from the output and inspect it (replace the placeholder with the actual partition path):

```sh
sudo cryptsetup luksDump /dev/REPLACE_WITH_LUKS_PARTITION
```

The header must report `Version: 2`. Confirm the decrypted mapping contains the Btrfs system volume. Check swap with `swapon --show`: zram may already be enabled by Archinstall, but there must be no disk-backed swap. Do not configure hibernation or a resume device.

If the system does not request a LUKS passphrase, the header is not LUKS2, or the root filesystem is not Btrfs inside the encrypted mapping, stop and correct the VM install before proceeding.

## Provision the installed system

Clone this repository to a stable location on the installed system, then run
`install/provision.sh` as the regular account that should own the desktop. The
script installs the declared system and desktop configuration through Ansible;
it does not run Archinstall or change the disk layout. Review the summary before
continuing. See [Ansible provisioning](../../ansible/README.md) for the role
details and [manual application installation](../manual-apps/README.md) for the
four packages that remain separately reviewed and installed.
