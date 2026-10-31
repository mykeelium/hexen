# VM-first Arch installation

This repository is built and proven in a disposable VM before it is used on a laptop. Never point Archinstall at a disk that contains data you need. The install process erases the selected target disk.

## Create the disposable VM

For the libvirt VM creation command, graphical-console access, and SSH bootstrap,
follow the [VM development workflow](vm/README.md). See the
[2026-10-25 investigation record](archinstall/observations-2026-10-25.md) for
installation evidence and the [resume note](../docs/resume.md) for current state.

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

After first boot, follow the [public quickstart](../docs/quickstart.md): clone
this repository to its long-term location and run [`first-boot.sh`](first-boot.sh)
(add `--vm` in a VM) as the regular desktop account. Choose Walker or Fuzzel;
first-boot setup prepares Walker if selected, then runs
[`provision.sh`](provision.sh). It audits boot
and applies the repeatable Ansible roles after showing an interactive summary.
The four manually reviewed third-party applications still follow their separate
procedure in [`manual-apps/README.md`](manual-apps/README.md).

Standalone provisioning asks which launcher to configure. Walker is the default.
When running standalone provisioning, first follow
[`manual-apps/walker/README.md`](manual-apps/walker/README.md) to review, build,
inspect, and install the pinned Walker/Elephant packages if selecting Walker.
The first-boot script guides this review and installation. The provisioner checks
the prerequisite; it does not build or install AUR recipes. Fuzzel comes
from Arch's signed repositories. Both choices route Super+Space,
Super+Escape, the Hexen menu, and the clipboard picker through the selected
launcher. Re-running provisioning lets you choose again; an older backend's
config link can remain on disk but is not used by the selected dispatcher.
If Walker's user service is already running, it remains until logout; the
provisioner does not terminate processes in the active desktop session.

Follow the [recovery guide](../docs/recovery.md) for checkpoint and offline
recovery procedures, including their current validation status.

## Laptop readiness gates

For a rehearsal guest using libvirt's default NAT uplink, run
`./install/provision.sh --vm` instead of the workstation invocation. This leaves
nested libvirt networks unmanaged to avoid the uplink subnet collision, selects
the `vulkan-virtio` driver required by Zed for the virtual GPU, and still
configures virtualization sockets and storage. The physical workstation must
select a Vulkan driver that matches its actual GPU. Choose Walker after
installing its separately reviewed packages, or choose Fuzzel if you prefer
the official-repository launcher. Bluetooth remains
enabled for future hardware, but its service is started only when its kernel
hardware directory exists. Keep the same mode and launcher on repeat runs.

The laptop is not ready to wipe yet. Before replacing its current OS:

- Complete VM update/reboot, root snapshot recovery, and repeatable provisioning.
- Install and verify the selected applications, Hyprland configuration, and
  the owner's Neovim configuration; test Zoom audio/video, whole-desktop
  sharing, and OBS recording with the actual Bluetooth headset and camera.
- Keep independent copies of required keys and documents, and verify access.
- Identify the laptop's GPU, Wi-Fi, storage controller, firmware, and UEFI needs;
  the VM does not validate those devices or suspend behavior.
- Confirm hardware virtualization is enabled and size VM memory/storage for the
  Windows lab. Keep its guests on a dedicated libvirt network, not a physical
  LAN bridge; see [virtualization guidance](../docs/virtualization.md).
- Verify official installation media boots on the laptop and that network
  access works before selecting any disk for installation.
- Confirm the disk identity and that the encryption passphrase is available
  independently of the system being replaced.

## References

- [Arch Linux downloads](https://archlinux.org/download/)
- [Arch Boxes (official VM images)](https://gitlab.archlinux.org/archlinux/arch-boxes)
- [Arch Wiki: QEMU](https://wiki.archlinux.org/title/QEMU)
- [Arch Wiki: Installation guide](https://wiki.archlinux.org/title/Installation_guide)
