# Personal Arch System Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build an understandable and repeatable Arch setup, prove it in a VM, and prepare it for a later full replacement of Linux Mint on the user's work laptop.

**Architecture:** Use Archinstall for a UEFI/GPT base install with a LUKS2-encrypted Btrfs system volume; keep disk selection and credentials interactive. Configure Limine and its kernel-update path explicitly. Use Ansible for repeatable system provisioning, and version user-owned Hyprland, Neovim, and theme files in the repository.

**Tech Stack:** Arch Linux, Archinstall, LUKS2, Btrfs, Limine, Snapper, Ansible, Hyprland, Neovim with the owner's configuration, zram.

**Spec:** `docs/superpowers/specs/2026-10-21-personal-arch-system-design.md`

## Global Constraints

- Full disk encryption is mandatory: LUKS2 protects the system volume; document that the UEFI EFI System Partition is unencrypted.
- UEFI and GPT are required for the initial supported install path.
- Never store disk passphrases, recovery keys, credentials, or other secrets in this repository.
- The Archinstall configuration and Ansible playbook must not silently choose or format a physical laptop disk; disk selection remains an explicit human action.
- Ansible must not repartition, format, or modify the disk layout and must be safe to run repeatedly.
- Use zram; do not configure hibernation or unencrypted disk swap.
- Use Btrfs with root snapshots managed by Snapper; snapshots are local recovery aids, not backups.
- Do not install Omarchy's theme platform or import a broad unreviewed configuration bundle.
- Declare application sources; prefer official Arch repositories, use vendor repositories or AUR only when required, and inspect AUR build instructions before installation.
- Target repeatable desired configuration, not bit-for-bit or exact-version reproducibility on Arch rolling release.
- Validate in a VM before any laptop installation; VM validation does not replace laptop-specific graphics, Wi-Fi, firmware, and UEFI checks.

## Review Focus

- **Wrong disk selected or erased:** Keep disk selection interactive; verify the chosen VM target with `lsblk` before installation and never test the install against a host disk.
- **Encryption or swap is incomplete:** After VM install, inspect `lsblk -f`, `cryptsetup luksDump` for LUKS version 2, `/etc/fstab`, and `swapon --show`; confirm boot asks for the LUKS passphrase and swap is zram.
- **Limine stops booting after a kernel update:** The boot update mechanism must be documented and verified with a VM update followed by a reboot.
- **Provisioning introduces drift or leaks secrets:** Run Ansible twice, inspect the second run for unexpected changes, and scan committed configuration for credential files or literal secrets.
- **An app is installed from an opaque or unsigned source:** Review the source matrix and, for each AUR package, inspect its `PKGBUILD` and upstream source before building it.

---

### Task 1: Establish a disposable VM install path and Archinstall profile

**Files:**
- Create: `install/README.md`
- Create: `install/archinstall/choices.md`
- Create: `install/archinstall/README.md`

**Interfaces:**
- Consumes: approved choices in the spec.
- Produces: a documented interactive Archinstall flow with a checked-in record of non-machine-specific choices; target disk and all credentials remain interactive.

- [x] **Step 1: Confirm the VM image role and create a disposable install target**

  Determine whether the downloaded Arch QCOW is an installer image or a preinstalled VM image. If it is preinstalled, boot the official Arch installation ISO and attach a separate blank QCOW disk as the disposable target. Document the VM firmware mode, target disk, and how to discard/recreate it.

- [x] **Step 2: Create `install/README.md`**

  Document VM creation, UEFI mode, installer media, target disk identification with `lsblk`, network access, and the rule that all destructive installation work is first performed only on the disposable VM disk.

- [x] **Step 3: Record the Archinstall choices in `install/archinstall/choices.md`**

  Use the guided Archinstall TUI to set UEFI/GPT, Btrfs, LUKS2 encryption, the selected base kernel, networking, locale, and user setup. Record the stable choices and prompts in `choices.md`. Keep the target disk, LUKS passphrase, and account credentials interactive on every installation; do not check in an Archinstall credentials file or a device-specific disk layout. If a reusable Archinstall JSON profile is later used, first prove in the VM that it preserves an explicit interactive disk-selection barrier and does not silently skip encryption.

- [x] **Step 4: Document the configuration and install procedure in `install/archinstall/README.md`**

  Include the exact Archinstall command, the choices recorded in `choices.md`, which prompts remain interactive, how to verify the selected device before committing disk changes, and how to confirm encryption after install. Explain that the EFI System Partition remains unencrypted and contains only boot files.

- [x] **Step 5: Walk through installation safely**

  Walk through the guided installation in the VM and stop at the final confirmation screen. Expected: the selected disk is the disposable VM disk, the encryption choice is visible, and install has not yet been confirmed. Inspect repository files to confirm no credentials or device-specific disk layout were recorded.

---

### Task 2: Audit Archinstall-owned Limine and prove encrypted boot across updates

**Files:**
- `install/limine/README.md`
- `ansible/roles/boot/tasks/main.yml`
- `ansible/roles/boot/tasks/validate-config.yml`
- `tests/boot.yml`
- `tests/boot-config.yml`

**Interfaces:**
- Consumes: the installed Archinstall UEFI/LUKS2/Btrfs system with a mounted ESP.
- Produces: a read-only boot audit before provisioning and documented update evidence.
- Ruling: Archinstall owns boot files and its package hook. A second Ansible
  writer would create conflicting ownership; the role discovers the actual root
  identifiers and audits the supported layout without a runtime UUID input.

- [x] **Step 1: Verify Archinstall Limine support for encrypted Btrfs**

  Archinstall 4.5 and Limine 12.9.4 boot the VM with mapper `root`, subvolume `@`,
  and the EFI application/configuration in `/boot/EFI/arch-limine/`.

- [x] **Step 2: Audit saved and running kernel parameters**

  Validate the actual LUKS UUID or PARTUUID and require unique root/encryption
  parameters in one complete entry. Keep machine identifiers out of shared files.

- [x] **Step 3: Document and audit update integration**

  The official kernel package rebuilds the initramfs; Archinstall's
  `99-limine.hook` redeploys the package EFI binaries. No AUR hook is needed.

- [x] **Step 4: Run read-only validation before base provisioning**

  Integration and malformed-configuration fixtures pass normally and in check
  mode. Boot artifacts are preserved and full provisioning reports zero changes.
  Independent review findings have been addressed with regression tests.

- [ ] **Step 5: Verify boot across an actual kernel upgrade**

  First boot and a host power-cycle reboot passed. On 2026-10-25, a full update
  found no newer packages. Reinstalling `linux` and `limine` exercised both real
  update hooks and its post-rebuild reboot passed. A future newer kernel
  transaction and reboot remain a separate acceptance check.

---

### Task 3: Add repeatable Ansible system provisioning

**Files:**
- Create: `ansible/ansible.cfg`
- Create: `ansible/inventory/localhost.yml`
- Create: `ansible/playbook.yml`
- Create: `ansible/group_vars/all/packages.yml`
- Create: `ansible/roles/base/tasks/main.yml`
- Create: `ansible/roles/base/handlers/main.yml`
- Create: `ansible/roles/base/templates/zram-generator.conf.j2`
- Create: `ansible/roles/base/templates/snapper-root.conf.j2`
- Create: `ansible/README.md`

**Interfaces:**
- Consumes: a booted Arch installation and repository-owned configuration.
- Produces: a local Ansible playbook using privilege escalation, explicit package lists, and idempotent configuration tasks.

- [x] **Step 1: Define a localhost inventory and playbook entry point**

  Target `localhost` with local connection and privilege escalation. Keep the first playbook free of role-specific desktop assumptions.

- [x] **Step 2: Add base package and service declarations**

  Base utilities, NetworkManager, zram, and Snapper are implemented and verified.
  The opt-in desktop role declares audio, portal, and user-session dependencies
  explicitly. `install/provision.sh` now provides the interactive entrypoint for
  the full workstation configuration.

- [x] **Step 3: Configure zram and no disk hibernation**

  Configure the selected systemd zram generator/package. Do not create swap partitions/files, hibernation hooks, or resume kernel parameters. Document verification with `swapon --show` and system configuration inspection.

- [x] **Step 4: Configure the Btrfs root snapshot layout and Snapper**

  Add a small documented Btrfs layout separating root from `/home`, initialize Snapper for root, and provide a clearly named command for creating a manual pre-update snapshot. Do not add automatic pacman hooks or AUR snapshot integrations.

- [x] **Step 5: Document run and rerun behavior**

  Add commands for installing Ansible from the official Arch repository, running the playbook, and checking syntax. State that the playbook never changes partitions or encryption and can be rerun after updates.

- [x] **Step 6: Check playbook syntax and repeatability in the VM**

  Run `ansible-playbook --syntax-check -i ansible/inventory/localhost.yml ansible/playbook.yml`, then run the playbook twice in the VM. Expected: syntax check succeeds; the second run has no unexplained changes or failures.

---

### Task 4: Inventory app sources and provision requested applications

**Files:**
- Create: `docs/app-sources.md`
- Create: `ansible/roles/apps/tasks/main.yml`
- Create: `ansible/roles/apps/defaults/main.yml`
- Modify: `ansible/playbook.yml`
- Modify: `ansible/group_vars/all/packages.yml`

**Interfaces:**
- Consumes: base package declarations and Ansible entry point from Task 3.
- Produces: an app source inventory and a repeatable installation role for the requested applications.

- [x] **Step 1: Research current package channels from primary sources**

  For Zen Browser, Neovim, Lazygit, Obsidian, 1Password, Zoom, and Slack, record in `docs/app-sources.md` the upstream download/documentation URL, chosen Arch installation source, package name, update path, and any AUR or vendor key/repository trust detail. Include plugins and tools downloaded by the owner's Neovim configuration. Prefer Arch official packages; use vendor repositories or AUR only when required. Do not select an unsigned third-party pacman repository when a reviewed AUR/Flatpak/vendor distribution is available.

- [x] **Step 2: Inspect every selected AUR package before enabling it**

  Review the `PKGBUILD`, install scripts, source URLs/checksums/signature checks, maintainer/upstream status, and expected update path. Record the review findings in `docs/app-sources.md`. Do not automate AUR builds or trust prompts in Ansible; provide explicit manual build instructions where required.

- [x] **Step 3: Add only reviewed package declarations**

  Use pacman modules for official repository packages. Keep manually installed AUR applications out of automatic package tasks. Include 1Password, Zoom, Slack, and Obsidian along with Zen, Neovim, and Lazygit using the sources selected in the matrix.

- [x] **Step 4: Attach the apps role to the playbook**

  The apps role now follows base and installs only Neovim, Lazygit, and Obsidian
  from official repositories. First run changed one task; second run changed zero.
  Remaining applications stay manual candidates per `docs/app-sources.md`.

- [x] **Step 5: Verify app provisioning in the VM**

  All requested apps are installed from the recorded official/manual sources.
  Manual source signatures/hashes, archives, privileges, and installed metadata
  were checked. Main provisioning still reports zero changes. First-launch,
  keyring, account, and meeting acceptance remain separate Task 6 gates.
  See `install/manual-apps/` for exact VM artifact records and procedure.

---

### Task 5: Add user-owned Hyprland, theme, and Neovim configuration

**Files:**
- Create: `config/hypr/hyprland.lua`
- Create: `config/hypr/theme.lua`
- Create: `config/waybar/config.jsonc`
- Create: `config/waybar/style.css`
- Create: `config/fuzzel/fuzzel.ini`
- Create: `config/mako/config`
- Create: `config/foot/foot.ini`
- Create: `config/nvim/README.md`
- Create: `config/nvim/` (the owner's configuration and selected plugin specs)
- Create: `ansible/roles/desktop/tasks/main.yml`
- Create: `ansible/roles/desktop/defaults/main.yml`
- Modify: `ansible/group_vars/all/packages.yml`
- Modify: `ansible/playbook.yml`

**Rulings from implementation:**
- Use current Hyprland 0.56 Lua syntax rather than the deprecated config syntax.
- Keep Omarchy's core key locations in an editable `bindings.lua`, translating
  framework helpers to explicit native commands. Record deviations in desktop.md.
- Use official Fuzzel initially; Walker/Elephant need separate manual source review.
- The owner selected Base plus the union of Numen/Arcana, not the local Omarchy
  LazyVim default. Source commit and merge decisions are recorded in config/nvim.

**Interfaces:**
- Consumes: installed Hyprland, Wayland support packages, Neovim, and application paths from Tasks 3–4.
- Produces: repository-owned desktop/editor configuration and a role that links or copies it to the user's home directory without overwriting unrelated user files.

- [x] **Step 1: Capture the user's selected workflow and keybindings**

  Inspect the current Omarchy keybinding configuration with the user and record only bindings they identify as useful. Do not copy unrelated Omarchy configuration or theme assets.

- [x] **Step 2: Create a minimal, commented Hyprland configuration**

  Add startup, monitor fallback, input, window/workspace navigation, application launch, and session lock/exit bindings. Keep bindings in one readable section and put colors/fonts/spacing in `theme.conf`.

- [x] **Step 3: Add a repository-owned theme foundation**

  Use named color variables and a small palette applied consistently to Hyprland, Waybar, Walker, Mako, and Foot. Do not fetch or install an external theme framework.

- [x] **Step 4: Add the owner's Neovim configuration and plugin selection**

  Use the owner's existing Neovim configuration as the source of truth. Confirm its location or repository before importing it; do not substitute a starter distribution. Keep plugin specs and lockfiles where that configuration expects them, and document how plugins, language servers, and other downloaded tools are installed and updated.

- [x] **Step 5: Provision user configuration without destructive overwrite**

  Add desktop role tasks that create required directories and link/copy only the repository-managed files. Back up or refuse to replace existing destination files that are not already managed by this setup.

  The role also installs the official OpenVPN/NetworkManager client stack and
  the virt-manager QEMU/KVM packages, then enables libvirt sockets, default NAT
  networking, and the persistent default VM storage pool. GOAD-specific provider
  automation remains outside this host setup until its local configuration is
  available for review.

- [ ] **Step 6: Verify the desktop in the VM**

  Partial acceptance passed on 2026-10-26: real workspace/terminal/launcher/editor
  and fullscreen shortcuts, visible editor/Obsidian setup, theme rendering,
  healthy portal/audio services, and a temporary Go LSP/DAP project. Remaining
  third-party apps and complete interaction/meeting checks keep this gate open.

  Log into Hyprland, confirm configured bindings launch the expected applications and navigate workspaces/windows, confirm theme files load, and open Neovim to confirm the owner's configuration loads the selected plugin specs.

---

### Task 6: Document snapshot recovery and complete VM acceptance

**Files:**
- Create: `docs/recovery.md`
- Modify: `install/README.md`
- Modify: `ansible/README.md`
- Modify: `docs/app-sources.md`

**Interfaces:**
- Consumes: encrypted VM system, Limine setup, Snapper root configuration, and application source inventory.
- Produces: an end-to-end recovery/acceptance guide and a clear checklist for deciding whether the laptop is ready for installation.

- [x] **Step 1: Document manual pre-update snapshot and recovery**

  Provide the exact Snapper command to create a named root snapshot before an update and the steps to boot Arch media, unlock LUKS, mount Btrfs top-level, restore the selected root snapshot, verify `/etc/fstab` and kernel command line, rebuild initramfs if required, and reboot. Clearly identify which step is destructive and how to preserve the failed root for diagnosis.

- [x] **Step 2: Exercise snapshot recovery in the VM**

  Passed on 2026-10-26: restored snapshot 1 offline, retained the old root,
  preserved home and nested subvolumes, restored matching ESP files, and booted
  the new root. Snapper could create another snapshot; provisioning was unchanged.
  See `docs/recovery.md` for evidence and the actual package-update limitation.

- [ ] **Step 3: Complete the VM acceptance checklist**

  Confirm encrypted boot, Ansible repeatability, all requested apps,
  Hyprland/theme/Neovim configuration, snapshot recovery, and a normal
  update/reboot. The four non-repository apps reached their sign-in/welcome
  screens and the owner will handle account sign-in separately. Launch Zoom and
  confirm the required screen-sharing path through the Wayland portal. Check
  logs for failed services and confirm no plaintext disk credentials were
  written to tracked files.

- [x] **Step 4: Document laptop readiness gates**

  Add a concise pre-install checklist for separate copies of keys/documents, identifying laptop Wi-Fi/GPU/firmware and UEFI behavior, confirming the user has Arch install media and can boot it, and confirming the encryption passphrase is safely available. State that a VM pass does not validate hardware-specific behavior.

- [ ] **Step 5: Review the complete repository configuration**

  Inspect all tracked files and app source records for secrets, unexplained dependencies, unreviewed AUR packages, destructive commands, or duplicated configuration. Expected: every downloaded/third-party source and every system-changing task is explicit and documented.

---

## Implementation References

- Archinstall configuration and credentials: [Archinstall upstream documentation](https://github.com/archlinux/archinstall)
- Disk encryption and boot partition: [Arch Wiki full disk encryption](https://wiki.archlinux.org/title/Full_disk_encryption)
- Limine and kernel entry automation: [Arch Wiki Limine](https://wiki.archlinux.org/title/Limine)
- Btrfs and Snapper layouts/recovery: [Arch Wiki Btrfs](https://wiki.archlinux.org/title/Btrfs), [Arch Wiki Snapper](https://wiki.archlinux.org/title/Snapper)
- Application install methods change over time; use each vendor's current documentation and the Arch package/AUR metadata at implementation time.
