# Ansible provisioning

The playbook configures an already installed Arch system. It does not partition, format, change encryption, or create firmware NVRAM entries. It installs Limine and writes its EFI binary/config only after checking the configured mountpoint is a mounted FAT GPT EFI System Partition. Review the roles before running them with privilege escalation. Supply the machine's LUKS UUID as a runtime variable; it is not a secret and is not stored in the repository.

Install Ansible from the official Arch repositories, then run from the repository root:

```sh
sudo pacman -S ansible
ansible-playbook --syntax-check -i ansible/inventory/localhost.yml ansible/playbook.yml
ansible-playbook -i ansible/inventory/localhost.yml ansible/playbook.yml --ask-become-pass -e boot_luks_uuid=YOUR_LUKS_UUID
```

Roles are intended to be repeatable. Review Ansible's reported changes on every run. The base role enables NetworkManager and sets up memory-backed zram; it does not configure hibernation or disk swap. Verify the result with `swapon --show` and inspect `/etc/systemd/zram-generator.conf`.

The base role creates Snapper's `root` configuration on a Btrfs root if one does not exist. It verifies `/home` is a separate Btrfs subvolume and refuses to proceed if `/.snapshots` is already a separate mount point. This protects Archinstall layouts that provision their own snapshots subvolume; inspect and reconcile that layout manually before rerunning. The role only removes an empty `/.snapshots` mountpoint directory when creating the initial Snapper config; it never unmounts or deletes a subvolume. Snapshots stay local and are not backups. Create a named manual pre-update snapshot with:

```sh
sudo snapper -c root create --description "before-system-update" --type single
```

The initial role does not install automatic pacman snapshot hooks. Review Snapper's retention settings before relying on cleanup behavior. The zram generator configuration limits the device to half of RAM, capped at 4 GiB; it has no backing disk or resume configuration.
