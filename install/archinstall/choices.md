# Archinstall choices

This is a human-readable record of the stable installation choices. Archinstall's menu names and configuration format can change between ISO releases; check the current screen and upstream documentation before confirming an install. Do not commit an exported credentials file or a disk layout tied to one machine.

| Area | Choice | Notes |
| --- | --- | --- |
| Firmware / partition table | UEFI with GPT | The VM and laptop must boot in UEFI mode for the supported path. |
| Target disk | Select interactively | Confirm the device with `lsblk`; never hardcode `/dev/vda`, `/dev/sda`, or a laptop-specific path. |
| EFI System Partition | Unencrypted FAT32 | Required for UEFI boot. Keep it limited to boot files. |
| System volume | LUKS2 | Set an interactive passphrase; do not save it in the repo or an exported credentials file. |
| Filesystem | Btrfs inside LUKS2 | Use root subvolume `@` and separate `/home` subvolume `@home`; do not place user files in a root snapshot. Record every mountpoint and subvolume shown in the summary. If Archinstall creates a separate `/.snapshots` mount, the base role deliberately stops until that layout is reconciled with Snapper. |
| Bootloader | Limine | Current Archinstall docs list Limine as a supported UEFI bootloader. Select it only if the current ISO's final summary shows the encrypted-root configuration; otherwise choose no bootloader and follow [`../limine/README.md`](../limine/README.md). |
| Kernel | `linux` | Start with the standard kernel; add a second kernel only if it has a clear recovery purpose. |
| Swap | zram, no disk swap | In the 2026.10.01 ISO VM walkthrough, Archinstall's Swap menu had zram enabled by default. Keep it enabled if the current ISO presents that default; never add a swap partition or file. Verify after boot. |
| Network | NetworkManager | Configure for the target system; avoid copying the installer environment's Wi-Fi credentials into tracked files. |
| User | Create a regular administrative user | Enter credentials interactively. Keep the root account disabled unless a specific recovery need is identified. |
| Locale / timezone / keyboard | Choose for the machine owner | These values can be recorded here after the first VM install if they should be shared across machines. |
| Additional packages | Minimal | Provision packages through the Ansible declarations after the base system boots. |

## Checks before confirming installation

1. The only selected target is the disposable virtual disk.
2. The partition layout leaves an EFI System Partition and encrypts the system volume with LUKS2.
3. The chosen filesystem is Btrfs. The guided partition flow also offers compression and default subvolume options; record the exact resulting layout from the final summary before confirming. Verify `@` for `/` and a distinct `@home` for `/home`.
4. No disk swap or hibernation setup is selected. zram is memory-backed and does not store a hibernation image.
5. The intended user, locale, keyboard, and timezone are correct.
6. The summary confirms `/boot` is the EFI mountpoint and records whether `/.snapshots` is mounted separately.
7. The summary shows the selected target and intended encryption before confirming the destructive operation.

After the first boot, verify the LUKS version using `cryptsetup luksDump` on the encrypted partition; the output must report `Version: 2`. Do not continue to the laptop install if encryption or boot differs from this record.
