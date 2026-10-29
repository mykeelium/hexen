# Ansible provisioning

The installed VM passed boot-role integration tests in normal and check mode.
The full playbook passed syntax validation and two provisioning runs; the
second run reported zero changes. Offline root/ESP recovery and its final reboot
passed. Current kernel/Limine reinstall hooks and reboot passed; a true newer-kernel
upgrade remains untested. See the [investigation record](../install/archinstall/observations-2026-10-25.md)
and [resume note](../docs/resume.md).

Run the playbook inside the target Arch VM during development, not on the host.
It does not partition, format, change encryption, create firmware entries, or
write boot files. Archinstall owns Limine's files and update hook. The boot role
audits that setup first, before the base role changes packages or configuration.
It discovers root identifiers from the running encrypted mapping; there is no
runtime UUID argument.

The supported initial boot contract is x86_64 UEFI, LUKS2 directly containing
Btrfs, mapper `root`, root subvolume `@`, a FAT GPT ESP at `/boot`, and a
non-UKI Linux entry in `EFI/arch-limine/` using mkinitcpio's `encrypt` hook.
Unsupported layouts fail validation instead of being rewritten.

The configuration audit deliberately supports one complete flat Limine entry,
unique root/encryption parameters, one simple `HOOKS=(...)` assignment with the
supported hook order, and the observed Archinstall Limine copy hook. It verifies
the default `linux` preset uses the audited configuration, kernel, and initramfs;
mkinitcpio drop-ins, alternate presets, and custom shell configuration are outside
this contract. Review those changes explicitly before extending the validator.

The `apps` role runs after `base` and installs Neovim, Lazygit, Obsidian, and
OBS Studio from official repositories. Its default package list is in
`roles/apps/defaults/main.yml`. See the [application source inventory](../docs/app-sources.md)
for versions, trust details, manual-install candidates, and remaining checks.
It does not install editor plugins or replace user configuration.

For a fresh install, clone this repository to a stable location and run
[`install/provision.sh`](../install/provision.sh) as the regular desktop account.
It shows the target and planned actions, downloads the declared Ansible
collection, checks playbook syntax, and runs the full base and desktop setup.
Keep the clone at that path after provisioning because the user's configuration
links point into it. If Ansible is missing, first run `sudo pacman -Syu ansible`
and reboot if the update replaced the kernel or another component that needs a
restart.

The equivalent commands from the repository root are:

```sh
sudo pacman -Syu ansible
export ANSIBLE_CONFIG="$PWD/ansible/ansible.cfg"
ansible-galaxy collection install -r ansible/requirements.yml
ansible-playbook --syntax-check -i ansible/inventory/localhost.yml ansible/playbook.yml
ansible-playbook -i ansible/inventory/localhost.yml ansible/playbook.yml \
  -e desktop_user="$(id -un)" --ask-become-pass
```

After a system update, `hexen update` can offer the provisioner in review mode.
It runs the same dependency and syntax checks, then Ansible check mode with
diffs, and requires a second confirmation before applying the playbook. Check
mode is advisory because command-based tasks may be skipped or may not predict
their full effect. Review the output and tracked configuration changes; the
playbook may start or reload configured services. It never reboots. Use
`hexen update --vm` when the target is the nested VM so the default libvirt
network remains unmanaged.

Roles are intended to be repeatable. Review Ansible's reported changes on every run. The base role enables NetworkManager and sets up memory-backed zram; it does not configure hibernation or disk swap. Verify the result with `swapon --show` and inspect `/etc/systemd/zram-generator.conf`.

The base role creates Snapper's `root` configuration on a Btrfs root if one does not exist. It verifies `/home` is a separate Btrfs subvolume and refuses to proceed if `/.snapshots` is already a separate mount point. This protects Archinstall layouts that provision their own snapshots subvolume; inspect and reconcile that layout manually before rerunning. The role only removes an empty `/.snapshots` mountpoint directory when creating the initial Snapper config; it never unmounts or deletes a subvolume. Snapshots stay local and are not backups. Create a named manual pre-update snapshot with:

```sh
sudo snapper -c root create --description "before-system-update" --type single
```

The initial role does not install automatic pacman snapshot hooks. Review Snapper's retention settings before relying on cleanup behavior. The zram generator configuration limits the device to half of RAM, capped at 4 GiB; it has no backing disk or resume configuration.

Use the [recovery guide](../docs/recovery.md) for a matching root/ESP checkpoint
and offline recovery. Root snapshots do not include `/boot`; a kernel rollback
must also reconcile the ESP. The documented restoration passed in the VM.

Run the boot integration test as root inside the installed disposable VM:

```sh
sudo env ANSIBLE_ROLES_PATH="$PWD/ansible/roles" \
  ansible-playbook -i localhost, tests/boot.yml
sudo env ANSIBLE_ROLES_PATH="$PWD/ansible/roles" \
  ansible-playbook -i localhost, tests/boot.yml --check
```

It accepts the working installation without UUID input, rejects an incorrect
ESP/root mapper, and checks that boot artifacts remain unchanged.

Run the configuration regression fixtures without root privileges:

```sh
ANSIBLE_ROLES_PATH="$PWD/ansible/roles" \
  ansible-playbook -i localhost, tests/boot-config.yml
```

These exercise the real role's configuration checks using in-memory fixtures.
They do not read or modify the machine's boot files. The suite includes a valid
installer configuration and conflicting parameters, split entries, hook
overrides, invalid update actions, and alternate initramfs configuration.


## Optional desktop and owner editor

Fresh OBS installation explicitly requests `pipewire-jack` in the same package
transaction so Pacman does not choose `jack2` before desktop provisioning. An
existing JACK installation still needs a reviewed migration; the playbook does
not remove conflicting user packages automatically.

Inside a guest whose uplink overlaps the default libvirt NAT subnet, use
`install/provision.sh --vm`. The wrapper passes the documented network override
to syntax checking and execution. Bluetooth service enablement is retained,
while a start attempt is skipped when the unit's hardware directory is absent.

Supply `-e desktop_user=YOUR_USER` to enable the desktop role after apps. See
[desktop setup](../docs/desktop.md) for local-TTY startup, editable bindings,
configuration protection, package details, and known differences from Omarchy.
The existing base-only invocation remains valid when this variable is omitted.
Existing user-owned parent directory permissions are preserved; symlinked or
foreign-owned parents and unmanaged destination configs are refused.
The entrypoint supplies the invoking regular user's name explicitly. The desktop
role installs LocalSend from an upstream AppImage pinned by SHA-256; it does not
install the four manually reviewed applications. Follow
[`install/manual-apps/README.md`](../install/manual-apps/README.md) separately.
Machine software profile selection and ignored per-machine package additions are
documented in [`docs/machine-profiles.md`](../docs/machine-profiles.md).
The base role installs the OpenVPN client; the desktop role adds its NetworkManager
plugin and the virt-manager/QEMU/KVM host stack. It enables modular libvirt
sockets and starts the packaged default NAT network. The desktop account is not
added to the broad `libvirt` group; system VM management uses Polkit. See
[`docs/virtualization.md`](../docs/virtualization.md) for the package inventory,
GOAD network isolation, and Windows guest notes.

The editor configuration is the owner's merged Base/Numen/Arcana source, with
[its own setup and source inventory](../config/nvim/README.md). Provisioning
links it but does not execute plugin/tool installation as root. Run its explicit
setup as the desktop user. Meeting/video/screen-sharing and complete project
language/debugger workflows still need acceptance testing.
