# Personal Arch System Design

## Goal

Build a transparent, repeatable Arch Linux setup that can be learned and validated in a virtual machine before replacing Linux Mint on the user's work laptop. The setup should carry over selected Omarchy workflow choices while keeping every installed component and configuration understandable and auditable.

## User goals and constraints

- The work laptop may be fully wiped and replaced; the user will separately preserve needed keys and documents.
- Full disk encryption is mandatory.
- The first target is a disposable UEFI VM installed from the official Arch ISO onto a blank QCOW2 disk; the work laptop is the next target.
- Limine is preferred over GRUB.
- Hyprland is preferred, including selected familiar keybindings, with a user-built theme rather than Omarchy's theming platform.
- Preferred applications: Zen Browser, Neovim with the owner's configuration, Lazygit, Obsidian, 1Password, Zoom, and Slack. LazyVim is not a required dependency.
- The setup should favor explicit, readable configuration and make package sources visible.
- The user prefers shutting down rather than hibernating. Initial setup should use zram and omit hibernation; encrypted hibernation can be considered later if needed.
- The user does not need an application/data migration guide. They do need to preserve selected documents and keys before wiping the laptop.

## Design

### Installation and provisioning

Use Archinstall for the base installation, keeping its non-secret configuration in the repository and the install process documented. Encryption passphrases, recovery keys, credentials, and other secrets must never be stored in the repository. The base installation creates a UEFI system with a LUKS2-encrypted system volume and Btrfs inside the encrypted volume. The verified Archinstall 4.5 path installs Limine, its static encrypted-root entry, and its EFI package-update hook. Archinstall owns those files; Ansible audits them before provisioning. Manual fallback instructions remain separate and unvalidated. Kernel/initramfs and EFI deployment are checked in the VM; an actual newer-kernel update/reboot remains an acceptance gate.

After first boot, use a readable Ansible playbook to install packages, configure services, and place system configuration. Ansible runs must be repeatable and should not repartition, format, or otherwise modify disk layout. Keep user-facing desktop configuration in plain files in the repository, separated from system provisioning so each is understandable on its own.

The goal is repeatable desired configuration across machines, not bit-for-bit reproducibility: Arch is rolling release software and package versions and third-party sources can change.

### Encryption and boot

- Require UEFI and GPT for the supported installation path.
- Encrypt the system volume with LUKS2 and unlock with a passphrase at boot.
- Keep the EFI System Partition unencrypted and limit it to firmware/boot files required to start the system. Document this exception to full disk encryption.
- Do not enable TPM-based automatic unlock in the initial version; it adds machine-specific behavior and reduces the simplicity of the initial audit.
- Configure Limine for normal boot and document its kernel/initramfs update integration.
- Do not configure hibernation initially. Use zram for swap; no unencrypted disk swap is permitted.

### Filesystem and recovery

- Use Btrfs inside LUKS2 with a small, documented subvolume layout that keeps the root system rollback separate from personal files.
- Configure Snapper for the root subvolume and document an explicit pre-update snapshot command. Do not add an automatic pacman snapshot hook in the initial version.
- Document recovery from an Arch installation medium by unlocking the encrypted volume, selecting/restoring a known-good root snapshot, and repairing boot configuration if needed.
- Treat snapshots as a local recovery aid, not as a backup. Require a separate copy of the user's keys and documents before the laptop is wiped.
- Automatic Limine menu entries for snapshots are not required for the initial implementation. Any AUR integration for that feature must be independently reviewed and explicitly justified.

### Desktop and applications

- Follow Omarchy's core default keybindings closely, as selected by the owner, in an editable repository-owned binding file. Translate required helpers explicitly and document omissions; do not import Omarchy's theme platform or an unreviewed configuration bundle.
- Build the theme from repository-owned configuration files.
- Declare each application and installation source. Prefer official Arch repositories. Use vendor repositories or AUR only when required, with the source and update behavior documented. AUR build instructions must be inspectable before use; do not pipe remote scripts directly into a shell.
- Include the user's requested applications: Zen Browser, Neovim with the owner's configuration, Lazygit, Obsidian, 1Password, Zoom, and Slack.
- Confirm each app's current official or community package channel during implementation, since distribution methods can change.

### VM-first acceptance path

The VM is the first supported target. Before moving to the laptop, the user should be able to:

1. Install the base system using the repository's documented Archinstall configuration and Limine steps.
2. Confirm boot requires the LUKS passphrase and reaches the graphical login/Hyprland session.
3. Run Ansible, then run it again without unintended changes or failures.
4. Confirm the requested applications, Hyprland configuration, and theme are present.
5. Create and recover from a root snapshot using the documented recovery process.
6. Apply a normal Arch update and reboot successfully.
7. Make a separate backup of the keys and documents needed from Mint.
8. Check laptop-specific graphics, Wi-Fi, firmware, and UEFI behavior before wiping Mint.

The VM cannot prove laptop-specific graphics, wireless, suspend, or firmware behavior; those require a hardware check before the final install.

## Out of scope for the initial version

- A graphical installer or a fully unattended disk-wiping script.
- TPM auto-unlock or Secure Boot enrollment.
- Hibernation.
- Exact package-version pinning or bit-for-bit reproducible images.
- Importing Omarchy's full configuration or theming platform.
- Migrating the user's files or application state automatically.

## Reference material

- Arch Wiki, [Archinstall](https://wiki.archlinux.org/title/Archinstall)
- Arch Wiki, [Full disk encryption](https://wiki.archlinux.org/title/Full_disk_encryption)
- Arch Wiki, [Limine](https://wiki.archlinux.org/title/Limine)
- Arch Wiki, [Btrfs](https://wiki.archlinux.org/title/Btrfs)
- Arch Wiki, [Snapper](https://wiki.archlinux.org/title/Snapper)
- Arch Wiki, [System maintenance](https://wiki.archlinux.org/title/System_maintenance)
