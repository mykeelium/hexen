# Hexen

A personal Arch Linux workstation setup: Archinstall for the base installation,
Ansible for post-install provisioning, and repository-owned Hyprland and Neovim
configuration. The target is repeatable configuration on a rolling-release
system, not identical package versions on every install.

## Try the developer preview

Start with the [public quickstart](docs/quickstart.md) and [known issues](docs/known-issues.md).
Use a disposable VM. The generated installer and new first-boot workflow still
need end-to-end acceptance before a release tag can be recommended.

## Current status

The repository contains a guided encrypted Archinstall procedure, a single
interactive provisioning entrypoint, and Ansible roles for boot validation,
base services, official applications, and the optional desktop/editor setup.
Encrypted boot, offline root/ESP snapshot recovery, and repeatable provisioning
passed in the VM. Neovim, Lazygit, and Obsidian install automatically from
official repositories. Zen, 1Password, Zoom, and Slack have reviewed manual
build/install procedures. VM testing recorded Zoom and 1Password launch failures; see the known issues
and application evidence before relying on them. Account integration, Zoom
screen sharing, newer-kernel upgrade, and hardware acceptance remain open.

The base setup includes OpenVPN through NetworkManager. The desktop role also
installs the virt-manager QEMU/KVM host stack; see
[VPN and virtualization setup](docs/virtualization.md) for its services,
authorization, network isolation, and GOAD resource notes.

For editable shortcuts and desktop startup, see [desktop setup](docs/desktop.md).
For the current stopping point and next actions, see [the resume note](docs/resume.md).
For day-to-day firewall, cache, backup, and hardware maintenance procedures, see
[maintenance](docs/maintenance.md). For the ordered pre-install and long-term
checklist, see the [workstation readiness roadmap](docs/operations-roadmap.md).

For development VM details, see the [VM development workflow](install/vm/README.md)
and [installation guide](install/README.md). The latest
[VM investigation record](install/archinstall/observations-2026-10-25.md) separates
tested behavior from source-code findings and remaining work.

Archinstall owns the boot files; Ansible validates that setup before applying
base configuration. Current kernel/Limine reinstall hooks and reboot passed;
an actual newer-kernel upgrade remains untested. See the
[recovery evidence](docs/recovery.md) and [application source inventory](docs/app-sources.md).

## Boundaries

- Use a disposable virtual disk for installation development.
- Keep disk selection, credentials, and destructive install confirmation interactive.
- Keep private keys, passwords, installer credential exports, and VM images out
  of the repository.
- Review package sources and enabled services explicitly.
- Validate boot, updates, provisioning repeatability, and recovery before using
  the setup on the work laptop.

The [design](docs/superpowers/specs/2026-10-21-personal-arch-system-design.md)
and [implementation plan](docs/superpowers/plans/2026-10-21-personal-arch-system.md)
describe the larger project. Neovim should use the owner's configuration;
LazyVim is not a required dependency.

## License

Original Hexen code is [MIT licensed](LICENSE). Included third-party material
retains its own terms; see the [notice inventory](docs/licenses/README.md).
