# Recovering the encrypted Btrfs root

Status: the disposable VM passed snapshot creation, boot-package hooks, the
post-rebuild reboot, offline root/ESP restoration, and the restored-system boot.
Provisioning remained repeatable. A newer-kernel upgrade and desktop/application
acceptance remain separate gates before installing on the laptop.

This guide applies to the verified layout: LUKS2 containing Btrfs subvolume `@`
at `/`, separate `@home`, `@log`, and `@pkg`, and a FAT ESP mounted at `/boot`.
Limine explicitly selects `subvol=@`; changing Btrfs's default subvolume with
`snapper rollback` does not change that explicit boot selection.

Snapshots are local checkpoints, not backups. Btrfs snapshots do not recurse
into nested subvolumes. Personal files, logs, package cache, nested machine
images, and Snapper's own snapshot store therefore require separate treatment.
See the [Btrfs subvolume documentation](https://btrfs.readthedocs.io/en/latest/Subvolumes.html)
and [Snapper manual](https://snapper.io/manpages/snapper.html).

## Snapshot retention policy

Hexen creates no automatic hourly timeline snapshots. The enabled
`snapper-cleanup.timer` service only cleans snapshots that were explicitly
created with a Snapper cleanup algorithm; it does not make the pre-update
recovery procedure below disposable. The root policy retains up to 10 regular
cleanup-managed snapshots and 5 cleanup-managed snapshots marked important,
with a seven-day minimum age before removal.

A pre-update checkpoint is a recovery pair: its Snapper root snapshot and the
matching `/boot` archive, checksums, and package manifest must remain together.
The procedure below deliberately creates a snapshot without a cleanup
algorithm, so Snapper will not remove it automatically. Do not add
`--cleanup-algorithm number` to that command. Review and remove an old recovery
pair only as a deliberate maintenance action, after confirming that another
known-good pair and an independent data backup exist. Snapper cleanup does not
know about the separate `/boot` archive.

For disposable, non-recovery checkpoints that are safe to prune, use the
`number` cleanup algorithm explicitly; these are bounded by the count and age
settings above:

```sh
sudo snapper -c root create --cleanup-algorithm number \
  --description "disposable-checkpoint"
```

This local policy is not an off-device backup. The separate `restic` package is
installed for future backup setup, but repository location, credentials,
schedule, retention, and restore acceptance still need to be configured.

## Before an update

Run inside the installed system. Choose a new destination on encrypted `/home`
for every checkpoint, and keep an independent backup of important personal data.
Close applications and avoid simultaneous package/configuration changes while
capturing the checkpoint. This is an administrative procedure, not a provisioner.

```sh
sudo -i
checkpoint=/home/ACTUAL_USER/recovery/CHOOSE_UNIQUE_CHECKPOINT
install -d -m 0700 "$checkpoint"
tar -C /boot -cpf "$checkpoint/boot.tar" .
pacman -Q > "$checkpoint/packages.txt"
findmnt --json > "$checkpoint/mounts.json"
btrfs subvolume list / > "$checkpoint/subvolumes.txt"
snapper -c root create --type single --description "before-system-update" \
  --userdata important=yes --print-number > "$checkpoint/snapshot-number"
find /boot -type f -exec sha256sum {} + > "$checkpoint/boot.sha256"
sync
pacman -Syu
```

The root snapshot includes the package database and installed modules, while the
archive captures the corresponding ESP kernel, initramfs, and Limine files.
Keep the archive and snapshot together. Root-only rollback after a kernel change
can otherwise leave the ESP kernel incompatible with the restored modules.
Inspect the transaction, reboot, unlock normally, and verify the boot audit,
networking, and failed-service list. A no-op update is not a newer-kernel test.

## Offline recovery from Arch installation media

Boot the official Arch ISO. Run these commands as root in its terminal. Replace
all uppercase placeholders using `lsblk -f`, `blkid`, the saved mount table, and
your known machine layout. Do not reuse `/dev/vda` names on a physical laptop.
Enter the LUKS passphrase interactively; never put it in commands or files.

```sh
lsblk -f
cryptsetup open /dev/ACTUAL_LUKS_PARTITION root
mkdir -p /mnt/btrfs
mount -o subvolid=5 /dev/mapper/root /mnt/btrfs
btrfs subvolume list /mnt/btrfs
```

The installed root must not be mounted or running during replacement. Mounting
the Btrfs top level makes the subvolumes explicit. Verify the selected snapshot
contains the expected `/etc/fstab`, package database, and kernel modules. Record
the snapshot number and a unique name for the failed root before proceeding.

```sh
top=/mnt/btrfs
snapshot=ACTUAL_SNAPSHOT_NUMBER
failed=@failed-CHOOSE_UNIQUE_NAME
test -d "$top/@/.snapshots/$snapshot/snapshot/etc"
test ! -e "$top/$failed"
cat "$top/@/.snapshots/$snapshot/snapshot/etc/fstab"
btrfs property get "$top/@/.snapshots/$snapshot/snapshot" ro
btrfs subvolume show "$top/@/.snapshots"
btrfs subvolume show "$top/@/var/lib/machines"
btrfs subvolume show "$top/@/var/lib/portables"
```

The following commands change which system boots. They preserve the failed root
instead of deleting it, but must only be run after selecting and inspecting the
correct snapshot. Run each command individually and stop on any error.

```sh
mv "$top/@" "$top/$failed"
btrfs subvolume snapshot "$top/$failed/.snapshots/$snapshot/snapshot" "$top/@"
```

The new writable `@` contains empty placeholders for nested subvolumes. Preserve
the existing Snapper store and machine-image subvolumes by moving them from the
retained root into those placeholders. The verified VM has the three paths
below; inspect `btrfs subvolume list` for additional nested subvolumes on another
installation. Do not recursively copy or delete them.

```sh
rmdir "$top/@/.snapshots"
mv "$top/$failed/.snapshots" "$top/@/.snapshots"
rmdir "$top/@/var/lib/machines"
mv "$top/$failed/var/lib/machines" "$top/@/var/lib/machines"
rmdir "$top/@/var/lib/portables"
mv "$top/$failed/var/lib/portables" "$top/@/var/lib/portables"
```

The failed root remains available for diagnosis, but its three nested subvolumes
now belong to the restored root. `@home`, `@log`, and `@pkg` remain at the Btrfs
top level and are not replaced.

Mount the restored system and its separate filesystems explicitly. Substitute
the real ESP partition and checkpoint destination.

```sh
mkdir -p /mnt/system
mount -o subvol=@ /dev/mapper/root /mnt/system
mount -o subvol=@home /dev/mapper/root /mnt/system/home
mount -o subvol=@log /dev/mapper/root /mnt/system/var/log
mount -o subvol=@pkg /dev/mapper/root /mnt/system/var/cache/pacman/pkg
mount /dev/ACTUAL_ESP_PARTITION /mnt/system/boot
checkpoint=/mnt/system/home/ACTUAL_USER/recovery/ACTUAL_CHECKPOINT
tar -tf "$checkpoint/boot.tar"
tar -C /mnt/system/boot -xpf "$checkpoint/boot.tar"
```

Only extract your own trusted matching checkpoint. Extraction restores archived
paths but does not remove files created by later package changes; inspect any
extras before proceeding. Do not format the ESP. Check that `/etc/fstab` and
`/boot/EFI/arch-limine/limine.conf` still identify the same root mapper and `@`.

```sh
cat /mnt/system/etc/fstab
cat /mnt/system/boot/EFI/arch-limine/limine.conf
arch-chroot /mnt/system sha256sum -c \
  /home/ACTUAL_USER/recovery/ACTUAL_CHECKPOINT/boot.sha256
arch-chroot /mnt/system pacman -Q linux limine mkinitcpio
arch-chroot /mnt/system cmp /usr/share/limine/BOOTX64.EFI \
  /boot/EFI/arch-limine/BOOTX64.EFI
arch-chroot /mnt/system snapper --no-dbus -c root list
```

Inside a recovery chroot, use Snapper's `--no-dbus` option: its service is not
running there.

A matching boot archive normally avoids a rebuild. If it is missing or
inconsistent, repair the kernel/initramfs and EFI deployment from the restored
system before rebooting; do not assume `mkinitcpio -P` installs a missing kernel
or repairs Limine. This repair path is not validated yet.

```sh
sync
umount -R /mnt/system
umount /mnt/btrfs
cryptsetup close root
poweroff
```

Remove the installation media, boot the restored disk, and unlock normally.
Verify root state reverted, personal files remained, Snapper can list and create
snapshots, networking works, and no services failed. Rerun the repository's boot
integration test and provisioning; provisioning should report zero changes.
Keep the failed root until you have verified recovery. No automatic deletion or
rollback command belongs in the shared Ansible playbook.

## Disposable VM acceptance record

The test checkpoint is in `/home/mcuomo/hexen-vm-recovery/`, with root snapshot
number recorded in `snapshot-number` and ESP archive `boot-before-update.tar`.
`/etc/hexen-recovery-probe` initially contains `before-recovery-test`;
`/home/mcuomo/hexen-recovery-home-probe` contains
`preserve-home-through-root-recovery`. A controlled change to the root marker
will be used to prove restoration, while the home marker must remain unchanged.

On 2026-10-25, `pacman -Syu` found no updates. Reinstalling the current `linux`
and `limine` packages exercised mkinitcpio and the EFI copy hook successfully.
The rebuild warned about optional firmware for `qat_6xxx`; boot validation
passed afterward. A true transition to a newer kernel remains untested.

The post-rebuild reboot passed: encrypted `@` root mounted, required services
were active, no services failed, and provisioning reported `ok=41 changed=0
failed=0`. The root probe was then changed to `changed-after-snapshot`.

On 2026-10-26, the owner unlocked the disk in the original Arch ISO. Snapshot 1
was restored to a new writable `@` (subvolume ID 264), preserving the previous
root as `@failed-recovery-test` (ID 256). The root probe reverted to
`before-recovery-test`, while the home probe remained unchanged. IDs of
`@home`, `@log`, `@pkg`, `.snapshots`, `var/lib/machines`, and
`var/lib/portables` were preserved. The package manifest matched the pre-update
checkpoint, all three saved boot-file checksums passed, and the EFI application
matched the installed package. Snapper listed snapshot 1 with `--no-dbus` in
the chroot. The restored filesystems were cleanly unmounted and LUKS closed.
The restored-system boot passed on 2026-10-26 with root ID 264, unchanged home
probe, matching boot hashes, active NetworkManager/SSH/guest agent, no failed
services, zram-only swap, HTTPS 200, and synchronized time. Snapper listed the
original snapshot and created snapshot 2, `hexen-after-successful-recovery`.
Boot integration tests passed normally and in check mode (`ok=46 changed=0
failed=0 rescued=2`), all 19 configuration fixtures passed (`ok=139 changed=0
failed=0 rescued=18`), and full provisioning passed (`ok=41 changed=0 failed=0`).
The previous root and both snapshots have not been deleted.
