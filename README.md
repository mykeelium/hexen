# Hexen

Welcome to Hexen! 

This is yet another prericed Arch setup. At the point we are 
with LLMs and documentation, code is cheap. I think there is going to be a 
stedy trend of each of us having our own, curated functionality that we can 
steer, so here is mine! I hope you enjoy.

I have personally like how streamlined the process can be, and the ability to 
make and use little tools to help make your PC more robust. But at the same time,
you do not have to trade off aesthetics to be able to get functionality.

Hexen is launching in open beta (might be more like alpha) to hit spooooky day!
It has been an ongoing process and more functionality and cleanup is in store!

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

## License

Original Hexen code is [MIT licensed](LICENSE). Included third-party material
retains its own terms; see the [notice inventory](docs/licenses/README.md).
