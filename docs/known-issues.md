# Developer preview: known issues

- The configuration-generating installer targets Archinstall 4.5 only. Its
  final clean end-to-end acceptance is pending. An assisted rehearsal passed
  encrypted boot, first-boot setup, graphical login, Walker and Firefox checks;
  see the [validation record](installer-preview-validation-2026-10-30.md).
  A clean run of the published revision and final mirror configuration is still
  required.
- The installer accepts only blank whole disks, at least 40 GiB. Existing
  partition tables/filesystems are refused, including previously installed
  test disks. It does not provide a wipe, dual-boot, or reinstall workflow.
- UEFI x86_64 only; Secure Boot, BIOS, RAID/LVM and multi-disk layouts are outside
  the supported preview. Physical hardware compatibility is not established.
- The generated preview supports the US keyboard layout only. Other layouts
  need a verified mapping across console, graphical login and lock screen.
- Walker and Elephant providers require reviewed source builds. First-boot
  setup now guides those builds, but can be slow and still requires inspecting
  community packaging recipes. AUR updates are not applied by pacman -Syu.
- Zen, 1Password, Zoom, Slack and Hyprmon remain separate manual installations.
  Firefox supplies browser access before Zen is installed.
- The recorded VM showed Zoom's “quit unexpectedly” report and 1Password's
  Crash Reporter with normal GPU launch. Disabling GPU acceleration reached
  1Password's welcome screen; this does not establish the cause or hardware
  compatibility. Zed's intended Vulkan acceleration remains unaccepted in that
  VM. See [application evidence](app-sources.md).
- A real newer-kernel upgrade/reboot remains unverified. Root snapshots and
  matching ESP recovery were rehearsed previously, but are not an independent
  backup of home data, credentials or VM disks.
- The configured GitHub repository is currently private. Public source/archive
  downloads cannot be accepted until publication is explicitly approved and a
  tested release revision exists.
- Configuration links depend on the checkout remaining at its installation
  path. Moving or deleting it can break the desktop.

These are preview limitations, not completed acceptance gates. The authoritative
remaining checklist is [the operations roadmap](operations-roadmap.md).
