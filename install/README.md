# VM-first Arch installation

This repository is built and proven in a disposable VM before it is used on a laptop. Never point Archinstall at a disk that contains data you need. The install process erases the selected target disk.

## Create the disposable VM

Use the official Arch Linux installation ISO as the boot medium. The QCOW2 files published by Arch's `arch-boxes` project are preinstalled basic or cloud images; they are virtual disks, not installation ISOs. If you want to keep the downloaded QCOW, leave it untouched and attach a separate empty virtual disk as the install target.

Suggested VM starting point:

- Architecture: x86_64
- Firmware: UEFI/OVMF
- CPU: 2 or more vCPUs
- Memory: 4 GiB or more
- Boot medium: current official Arch installation ISO
- Target: new 40 GiB or larger QCOW2 virtual disk, attached as the only writable disk
- Network: NAT is enough for installation and package downloads

In virt-manager, create a new VM, select the ISO as its installation medium, choose UEFI firmware, and add a new QCOW2 storage volume for the target. Do not attach host block devices or the work laptop's disk. Take a VM snapshot before installation if you want an easy reset point.

The VM disk can also be created from a terminal with `qemu-img create -f qcow2 arch-test.qcow2 40G`; attach that file as a virtual disk through your VM manager. Confirm that the path and filename are the disposable VM disk before using this command.

## Verify the installer and disk

Download the ISO and its signature/checksum only from [Arch Linux's official download page](https://archlinux.org/download/). Verify the downloaded ISO using the published signature or checksum before booting it.

Boot the ISO in UEFI mode. At the live shell, inspect disks with:

```sh
lsblk -o NAME,SIZE,TYPE,FSTYPE,MOUNTPOINTS,MODEL
```

Identify the blank virtual target by its size and model. It should be obvious and should not contain a mounted filesystem. If there is any ambiguity about which device is the disposable VM disk, stop before opening Archinstall.

Check that the live system has network access before installing packages. Do not copy Wi-Fi passwords, SSH keys, or other credentials into this repository.

## Install

Follow [`archinstall/README.md`](archinstall/README.md) and the non-secret choices in [`archinstall/choices.md`](archinstall/choices.md). Keep disk selection, encryption passphrase, user password, and final install confirmation interactive.

The EFI System Partition is necessarily unencrypted in this setup and contains only files needed to start the system. The system volume is protected by LUKS2 and requires a passphrase at boot.

## After installation

Before adding desktop configuration, confirm that the VM boots through Limine, requests the LUKS passphrase, and mounts the encrypted Btrfs root. Then use the repository's Ansible playbook. Do not attempt the laptop install until the documented VM acceptance steps in [`../docs/superpowers/specs/2026-10-21-personal-arch-system-design.md`](../docs/superpowers/specs/2026-10-21-personal-arch-system-design.md) have been completed and the laptop's hardware has been checked.

## References

- [Arch Linux downloads](https://archlinux.org/download/)
- [Arch Boxes (official VM images)](https://gitlab.archlinux.org/archlinux/arch-boxes)
- [Arch Wiki: QEMU](https://wiki.archlinux.org/title/QEMU)
- [Arch Wiki: Installation guide](https://wiki.archlinux.org/title/Installation_guide)
