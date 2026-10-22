# Limine on an encrypted Arch system

The intended path uses the official `extra/limine` package, a static Limine Linux entry, and Arch's regular kernel files (`/vmlinuz-linux` and `/initramfs-linux.img`). The kernel package updates these stable paths. The optional `limine-mkinitcpio-hook` package is in the AUR and is not used here; it is not needed for a single static entry. Secure Boot is out of scope for this first version.

The current Archinstall supports Limine as a bootloader choice. If the VM walkthrough confirms that its Limine option installs an encrypted-root entry correctly, use it. Otherwise choose no bootloader and apply these manual steps from the installed system or an Arch live ISO with the installed system mounted and chrooted. Do not install or copy boot files until the target ESP is verified.

## Required layout

- UEFI firmware and GPT.
- An unencrypted FAT32 EFI System Partition mounted at `/boot` (so the kernel and initramfs are available to Limine).
- A LUKS2 container holding Btrfs, with root mounted from subvolume `@`.
- The ESP is not encrypted; it contains the Limine EFI application, kernel, initramfs, and boot configuration. The system Btrfs volume is encrypted.

If the verified installation has a different ESP mount point or Btrfs subvolume name, adapt the paths and kernel command line before installing Limine. Never assume the VM and laptop have the same device path or LUKS UUID.

## Install Limine manually

Install the signed Arch repository package and verify the ESP is mounted:

```sh
sudo pacman -S limine efibootmgr
findmnt --mountpoint /boot
findmnt -no FSTYPE --mountpoint /boot
```

The second command must show `vfat`. Then create the application directory and copy the UEFI executable from the package:

```sh
sudo install -d -m 0755 /boot/EFI/limine
sudo install -m 0644 /usr/share/limine/BOOTX64.EFI /boot/EFI/limine/BOOTX64.EFI
```

Create a firmware entry with `efibootmgr` using the actual disk and ESP partition number from `lsblk` and `findmnt` (replace both placeholders):

```sh
sudo efibootmgr --create \
  --disk /dev/ACTUAL_WHOLE_DISK \
  --part ACTUAL_ESP_PARTITION_NUMBER \
  --label 'Arch Linux (Limine)' \
  --loader '\EFI\limine\BOOTX64.EFI'
```

This is machine-specific and must not be automated from the shared Ansible role. Alternatively, install the standard fallback path after checking that it will not overwrite another boot manager.

## Kernel command line and entry

Use [`etc-kernel-cmdline`](etc-kernel-cmdline) as the reviewed command-line template. Replace `REPLACE_WITH_LUKS_UUID` with the UUID from `cryptsetup luksUUID /dev/ACTUAL_LUKS_PARTITION`, and confirm that the installed initramfs has the `encrypt` hook. Do not include quotation marks around the UUID. The matching Ansible Limine template expects the UUID as the runtime variable `boot_luks_uuid`; supply it at playbook time rather than committing a host-specific value.

The configuration is rendered to `/boot/limine.conf`. Its `cmdline` must use the actual LUKS UUID, mapper name, and root subvolume. Verify the paths against `findmnt /boot` and `ls -l /boot` before rebooting.

## Updates and verification

The standard `linux` package updates `/boot/vmlinuz-linux` and `/boot/initramfs-linux.img`; the static Limine entry continues to reference those paths. Keep enough free space on the ESP and verify the files after each kernel update. After a Limine package update, manually copy the current `/usr/share/limine/BOOTX64.EFI` to `/boot/EFI/limine/BOOTX64.EFI` and verify the copy. The repository does not install an automatic package hook for this operation.

Before declaring the VM boot path ready, verify the firmware entry, Limine menu, LUKS passphrase prompt, Btrfs root subvolume, and successful boot. Then perform a normal kernel update and reboot again. Until that is proven in the VM, do not use this setup on the work laptop.

References: [Arch Wiki: Limine](https://wiki.archlinux.org/title/Limine), [Arch Wiki: full system encryption](https://wiki.archlinux.org/title/Dm-crypt/Encrypting_an_entire_system), [Arch Linux `limine` package](https://archlinux.org/packages/extra/x86_64/limine/), [Limine configuration reference](https://github.com/Limine-Bootloader/Limine/blob/v12.x/CONFIG.md).
