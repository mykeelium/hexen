# Guided Archinstall procedure

This procedure intentionally keeps destructive disk selection and all credentials interactive. A saved Archinstall disk configuration can point at a stale device name or omit the intended encryption settings; do not replay one blindly.

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
