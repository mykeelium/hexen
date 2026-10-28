# Hexen workstation readiness and lifecycle roadmap

**Purpose:** track the remaining work to make this Arch setup safe to install on
the work computer, easy to maintain, and reproducible across the owner's
machines. This is a checklist and design direction; it does not mean every
listed feature must exist before the first laptop install.

**Current model:** install a standard Arch system with Archinstall, then apply
this repository with Ansible. This is not a custom Arch ISO. Keeping the
official installer and a reviewable post-install repository is simpler to
update and recover; a custom ISO can be a separate project if it becomes useful.

## What already exists

- [x] Archinstall choices and a Limine/LUKS2/Btrfs boot contract are documented.
- [x] `install/provision.sh` is the interactive post-install entry point; Ansible
  installs declared packages and configures the machine.
- [x] The system and desktop roles are intended to be repeatable. Configuration
  links point into the repository, and preflight checks refuse unmanaged files.
- [x] Common, desktop, and application package lists are declared in Ansible.
  Package sources and manual installation procedures are recorded separately.
- [x] Named themes, wallpaper-based Matugen packs, and the guided theme builder
  live with the desktop configuration.
- [x] The merged Neovim configuration and plugin pins are in the repository.
- [x] In the VM, root snapshot recovery was exercised from Arch media, including
  restoring the matching EFI files. Provisioning and configuration regression
  checks have also passed.
- [ ] A true upgrade to a newer kernel and the resulting reboot have not yet
  been proven. Recent desktop/theme changes also need a fresh VM acceptance pass.
- [ ] The documented snapshot procedure is not an off-machine backup. Home data,
  VM images, credentials, and recovery material need a separate backup plan.

## Priority 0: finish the pre-install gates

These are the current blockers to wiping the work computer.

- [ ] **Rehearse a clean install from the current official Arch ISO.** Use a
  disposable VM disk, follow the Archinstall choices, boot through encrypted
  Limine, clone the repo to its intended permanent path, and run
  `install/provision.sh`. Record the exact point where manual application steps
  or user choices remain.
- [ ] **Exercise a real full system upgrade.** From a pre-update root snapshot
  and matching `/boot` archive, install an actually newer kernel, reboot, unlock,
  and confirm Limine, initramfs, NetworkManager, audio, desktop, and the
  provisioner's zero-change rerun. Reinstalling the same package is useful
  evidence, but is not a substitute for this newer-kernel transition.
- [ ] **Complete the laptop hardware inventory and live acceptance.** Identify
  GPU, Wi-Fi, Bluetooth, storage controller, firmware/UEFI behavior, camera,
  display layout/scaling, keyboard, touchpad, brightness keys, and suspend/resume.
  Test these on the target hardware; a VM cannot validate them.
- [ ] **Accept the real meeting workflow.** Pair the Bluetooth headset, complete
  a Zoom call, verify speaker/microphone/camera, share the whole Wayland desktop,
  and record/play back an OBS clip with the intended audio sources.
- [ ] **Verify work-account access and recovery.** Sign into the applications
  needed for work, confirm the FIDO authenticator and password manager work
  after a clean boot, and make sure account recovery does not depend on the old
  OS. Keep account tokens and private keys out of the repository.
- [ ] **Accept the Windows lab workload.** Create the required Windows VMs with
  virt-manager, check that memory/storage remain adequate for simultaneous
  guests, and verify the isolated libvirt network is not bridged to a work LAN.
- [ ] **Make and restore an independent data backup.** Confirm that personal
  files, existing VM disks, browser/editor data, SSH/GPG/FIDO recovery needs,
  and required work documents are copied somewhere other than this computer.
  Boot the recovery media and confirm the encryption passphrase and recovery
  instructions are available without relying on the machine being wiped.
- [ ] **Review the final package/source inventory.** Refresh the package and
  third-party source notes before installation. Keep signed Arch packages as
  the default. Explicitly decide which manually installed applications are
  required on the work computer and who updates them.
- [ ] **Capture a clean repository checkpoint.** Review `git status`, commit or
  intentionally retain the completed setup work, and make sure no credentials,
  local VM files, private wallpapers, or machine-specific secrets are tracked.

## Priority 1: make configuration changes easy to manage and distribute

The repository already is the central source for the configs it manages: the
desktop role links files from the clone, so editing a linked file edits the
repository copy. Git history is the distribution mechanism. The missing part is
a clear day-to-day workflow and explicit machine profiles.

- [ ] **Keep one source of truth initially.** Continue using this Git repo for
  Archinstall notes, Ansible roles, common desktop configs, themes, scripts, and
  docs. Use Ansible for system packages/services and deployment; use Git for
  reviewing and distributing edits. Avoid introducing a second dotfile engine
  until the current workflow has a demonstrated limitation.
- [ ] **Define profile layering.** Establish a documented precedence such as
  `common` → `numen` or `arcana` → ignored local override. Keep the user's
  requested inclusive core in common, put actual hardware-specific choices in
  the machine profile, and keep credentials and private machine data outside
  Git. Start with monitor/GPU/input/network settings and package differences;
  do not duplicate whole config trees when a small override is enough.
- [ ] **Add a Hexen config command group.** A small `hexen config` interface
  should provide:
  - `status`: show selected machine profile, repository revision/dirty state,
    and links that are missing or point somewhere unexpected.
  - `diff`: show local repository edits before sharing or updating.
  - `apply`: run the checked Ansible configuration path with a clear preview,
    retaining its current refusal to overwrite unmanaged user files.
  - `backup` or `restore`: copy a config aside before a deliberate migration or
    replacement. Never silently overwrite a user's edit.
- [ ] **Document the edit-and-share loop.** Make it explicit: edit through the
  linked config or in the repo, inspect `git diff`, validate the relevant config,
  commit, then update the other machine from the reviewed Git revision. Keep
  machine-local files ignored and provide examples of which settings belong in
  common versus a host profile.
- [ ] **Evaluate chezmoi only if scope grows.** Chezmoi is worth reconsidering if
  the project expands to many home-directory files, multiple operating systems,
  or templated secret handling. For the current Arch-only setup, adding it now
  would duplicate Ansible/Git responsibilities without solving a proven gap.

## Priority 1: complete the desktop capture workflow

Hexen currently binds Print to a `grim`/`slurp` region capture copied to the
clipboard. The owner wants a more complete screenshot workflow inspired by
[Omarchy's capture flow](https://omarchy.baris.sh/manual/screenshots-recording/).

- [ ] **Design and implement a useful screenshot flow.** At minimum, decide and
  support region, window, and full-display capture; save screenshots under
  `~/Pictures` and copy them to the clipboard; and provide a clear annotation
  path. Keep capture local and user initiated. Review Omarchy's capture menu,
  recording, color picker, and OCR features, and include only the extra modes
  that fit Hexen's needs. Document bindings, dependencies, save location, and
  tested behavior in the desktop guide.

## Priority 1: add a safe, single update entry point

Today, `pacman -Syu`, Git updates, Ansible provisioning, Neovim tools, and manual
application updates are separate procedures. A future `hexen update` should
coordinate the supported work and leave source changes reviewable. Omarchy's
current `omarchy update` is a useful reference for coordinating logs, locking,
space checks, snapshots, package updates, migrations, restarts, boot checks,
and reboot prompts in one visible workflow ([update process](https://github.com/omacom/omarchy/blob/quattro/docs/update-process.md),
[user guide](https://github.com/omacom/omarchy/blob/quattro/manual/30-updates.md)).
Hexen should use the parts that fit this setup; it should not automatically
build AUR packages or run unreviewed remote scripts.

- [ ] **Start with `hexen update --check`.** Report whether the repo has upstream
  commits, whether it is dirty or diverged, whether official package updates are
  available, and whether a reboot or config reconciliation is pending. This is
  read-only.
- [ ] **Implement the interactive `hexen update` path.** Proposed sequence:
  1. Acquire a lock, start a readable transcript log, check free space and
     whether another package operation is active.
  2. Check Git state. Stop on local edits or divergence; show the diff/commits
     and require a clean fast-forward before changing repo-owned configs.
  3. Confirm the update and capture a root snapshot plus a matching `/boot`
     archive. Clearly report if a safe checkpoint cannot be made.
  4. Run one complete `pacman -Syu` transaction. Never perform a partial
     system upgrade. Do not silently install packages from AUR or new package
     repositories.
  5. Run idempotent, resumable user-data/config migrations, then apply the
     reviewed repo's Ansible configuration to converge links and services.
     Finish with source-specific checks.
  6. Inspect `.pacnew`/`.pacsave` files, failed services, kernel/boot changes,
     and update errors. Explain which services need restart and whether a reboot
     is recommended; do not reboot without the user's confirmation.
  7. Return a clear success/failure status and point to the log and recovery
     checkpoint. A failed step must not be reported as a completed update.
- [ ] **Define rollback boundaries in the update UI.** The root snapshot does not
  include `/home`; `/boot` needs its matching archive. Roll back user config by
  reverting to a reviewed Git revision and reapplying it. Restore personal
  files from the separate backup. Never imply that a root snapshot alone rolls
  back all three.
- [ ] **Keep safe exits simple.** Initial version should not block normal Pacman
  use with an ALPM guard. If later adding a guard, test recovery shells,
  unattended maintenance, Ansible, and package-manager frontends first. Always
  retain a documented direct recovery route.
- [ ] **Separate update ownership.** Official Arch packages update through
  Pacman. Manual Walker builds, LocalSend's pinned AppImage, proprietary vendor
  apps, Neovim plugins, Mason tools, and language SDK tools have different
  sources. Give each an explicit owner and update procedure; show unsupported or
  manually reviewed updates as pending rather than pretending Pacman covers them.
- [ ] **Add a migration mechanism before changing user data automatically.**
  Numbered, idempotent migrations should be versioned with the repo and keep
  per-user completion markers under Hexen's state directory. They must be
  resumable after interruption, produce logs, and avoid changing user data
  during the Pacman transaction. Omarchy documents a similar post-package,
  per-user migration model and event hooks ([update process](https://github.com/omacom/omarchy/blob/quattro/docs/update-process.md),
  [dotfiles and hooks](https://github.com/omacom/omarchy/blob/quattro/manual/31-dotfiles.md)).
- [ ] **Add an update status indicator after the CLI is reliable.** A Waybar
  module or menu item can show available repo/package updates and launch
  `hexen update`; clicking it must not start a privileged transaction silently.

## Priority 2: operational resilience and maintenance

- [ ] **Add `hexen doctor`.** Read-only report for Arch release, repo revision
  and dirty state, profile, broken config links, package differences, active
  critical services, failed units, disk space, snapshots, boot artifacts,
  network, and pending migrations. Support a privacy-reviewed report file; do
  not upload logs automatically.
- [ ] **Create an off-device backup policy.** Snapshots protect against local
  rollback mistakes, not drive failure, theft, or accidental deletion. Define
  encrypted backup destinations and retention for home files, editor data,
  VM images, and recovery material. Test restoring representative files.
- [ ] **Finish boot rollback instructions.** The existing documented recovery
  restored a matching snapshot and ESP archive. The repair path when the saved
  boot archive is missing or inconsistent remains unvalidated; prove it in a
  disposable VM before automating any boot repair.
- [ ] **Track `.pacnew` and `.pacsave` files.** Report candidates after updates,
  show diffs, and let the owner merge them. Never replace an edited config
  automatically.
- [ ] **Decide firmware maintenance.** Document when to inspect LVFS/fwupd and
  laptop-vendor firmware, keep firmware separate from routine package updates,
  and require an explicit user action for firmware writes/reboots.
- [ ] **Add recovery-friendly package records.** Save package manifest, repo
  revision, profile, update log, boot hashes, and snapshot number together for
  each successful system update. Keep secrets and private config contents out
  of the record.
- [ ] **Set an upstream review cadence.** Recheck source URLs, signatures,
  checksums, AUR recipes, and out-of-date official package flags before
  changing their automation. Keep pinned third-party builds manual until the
  review/update path is reproducible and trusted.

## Suggested delivery order

1. Complete the P0 VM, recovery, application, hardware, and backup gates.
2. Add common/numen/arcana profile selection and the Git-based config status/diff
   workflow.
3. Build and exercise `hexen update --check`, then the logged, locked,
   snapshot-backed update path in the disposable VM.
4. Add idempotent migrations, `.pacnew` reporting, and `hexen doctor` as the
   update path exposes real needs.
5. Add the Waybar/menu update indicator and decide whether a broader dotfile
   manager or firmware helper is justified.
6. Only then install on the work computer, retaining the existing OS until the
   encrypted install, work apps, meetings, VM lab, backups, and rollback path
   pass on the target hardware.

## References

- [Hexen installation guide](../install/README.md)
- [Desktop and themes guide](desktop.md)
- [Recovery procedure and VM evidence](recovery.md)
- [Application sources and update paths](app-sources.md)
- [Virtualization and network isolation](virtualization.md)
- [Omarchy update-process internals](https://github.com/omacom/omarchy/blob/quattro/docs/update-process.md)
- [Omarchy update user guide](https://github.com/omacom/omarchy/blob/quattro/manual/30-updates.md)
- [Omarchy dotfiles, hooks, and extensions](https://github.com/omacom/omarchy/blob/quattro/manual/31-dotfiles.md)
