# Guided Archinstall procedure

This procedure intentionally keeps destructive disk selection and all credentials interactive. A saved Archinstall disk configuration can point at a stale device name or omit the intended encryption settings; do not replay one blindly.

## Run the guided installer

1. Boot the official Arch installation ISO in UEFI mode.
2. Run `lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,MODEL` and identify the blank virtual disk by size/model.
3. Start the installer with `archinstall`.
4. Follow [`choices.md`](choices.md), selecting the target disk interactively and configuring UEFI/GPT, an unencrypted EFI System Partition, LUKS2 encryption, and Btrfs for the system volume.
5. Select Limine if the current installer offers it and supports the chosen encrypted layout. If not, choose the installer's no-bootloader option and use the manual Limine procedure documented in `../limine/README.md` after the system is installed.
6. Enter the LUKS passphrase and user credentials at the prompts. Do not save an Archinstall `user_credentials.json` file in this repository. Archinstall's upstream docs distinguish general configuration from credentials because encryption passwords are sensitive.
7. Review the final summary carefully. The only target must be the disposable VM disk; verify the encryption and filesystem choices. Only then confirm the install.

Archinstall configuration names and menus change over time. The current upstream guided installer supports Limine, but this encrypted-root combination has not yet been confirmed in the VM. Use the current [guided installation documentation](https://archinstall.archlinux.page/installing/guided.html) and the options presented by the ISO rather than copying a stale JSON example. Before confirming, record the selected EFI mountpoint, Btrfs root and home subvolumes, any `/.snapshots` mount, and the encryption and bootloader choices.

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
