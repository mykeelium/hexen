# Candidate rehearsal progress — 2026-11-03

Candidate: `ef741912ab7a3f01cd6296a0e11efe643f5ec821` (public squash merge;
same tree as the previously tested `4b2367c`). This is partial acceptance.

## Environment

New VM `hexen-candidate-4b2367c-20261102`: UEFI, Secure Boot disabled,
4 CPUs, 8 GiB RAM, new blank 64 GiB Virtio disk. Existing VMs untouched.
Arch ISO 2026.10.01, Archinstall 4.5. ISO SHA-256 matched the official dated
checksum: `684ded26c63240ff4a41e8c25ee84ea6da233f557364821f13d12c2b0a9059a5`.
Synthetic account `trialuser`; no owner account credentials used.

## Passed

- All three GitHub CI jobs passed for the published candidate.
- Anonymous candidate archive download and installer preview passed.
- Interactive base installation completed without mirror repair or disabled
  package signature checks. LUKS2, separate Btrfs subvolumes and Limine verified.
- Installed-disk encrypted boot and ordinary account login passed.
- Permanent checkout matches the candidate on branch `hexen`, tracking
  `origin/main`.
- Cancellation before prerequisites returned 3 and preserved the package manifest.
  Cancellation at provisioning also returned 3 without setup-success output.
- Guided pinned Walker 2.17.2 and Elephant/providers 2.22.1 builds passed source
  verification and archive review. Retry reused the reviewed installed builds.
- First provisioning: `ok=189 changed=48 failed=0`. Health and actual Hyprland/
  Ghostty config validation passed.
- Reviewed rerun: check mode `ok=177 changed=0 failed=0`; real apply
  `ok=183 changed=0 failed=0`. Real Matugen 4.2 reported Tokyo Night unchanged.
- Firewall inspected as default/active `drop`, target `DROP`, only
  `dhcpv6-client`, no forwarding or broad inbound exceptions. No failed system
  or user units were reported before graphical reboot.
- SDDM reached UWSM-managed Hyprland after encrypted reboot; Waybar displayed.
- Super+Space opened Walker. Firefox app search and `1+1` → `2` were visible.
- Super+Shift+B opened Firefox. Super+Shift+Alt+B opened a visibly identified
  Firefox private window.
- Idle display-off and lock were observed. Waking showed Hyprlock; the synthetic
  account password returned to the running desktop.

## Remaining

The confirmed `hexen update --vm` workflow subsequently passed with exit status 0.
It created Snapper snapshot 1 and a matching EFI archive in
`/home/trialuser/recovery/hexen-updates/20261103T124527Z-26389574/`, then upgraded
libnm, NetworkManager, python-platformdirs, uv and python-uv. Optional Ansible
convergence was declined in this transaction (its no-op review/apply had already
passed separately). Service review identified NetworkManager's replaced files;
the explicitly approved restart passed, followed by HTTPS 200. Archive integrity
and all six recorded boot-file checksums passed before reboot. Encrypted reboot
then reached SDDM with the managed Hyprland session selected. No kernel upgrade
was offered, so this does not accept the newer-kernel transition. Offline
restoration was subsequently exercised as recorded below.

Offline recovery on 2026-11-03: booted the verified Arch ISO, interactively
unlocked the installed LUKS partition, inspected read-only snapshot 1 and its
filesystem layout, preserved the updated root as `@failed-rehearsal-20261103`,
then created writable `@` from the snapshot. The existing Snapper store and
`var/lib/machines`/`portables` subvolumes were moved into the restored root.
The matching EFI archive was verified inside the chroot and restored; all six
boot-file checksums and the Limine EFI/package comparison passed. The entire
restored package manifest matched `packages-before.txt`; NetworkManager reverted
to 1.58.1-2 and uv to 0.13.6-1. The home package-evidence probe retained SHA-256
`3b0136b266fa3b61867fdd4a4bc5a911e817a8d06c57f5a81ea532e7dc59d80e`.
Snapper listed the preserved checkpoint. An initial archive-check invocation
used installed absolute paths outside the chroot and failed to locate the file;
rerunning the verification inside the chroot passed before extraction.
After clean unmount/LUKS close and removal of recovery media, encrypted boot
reached SDDM and normal authentication returned to the managed Hyprland desktop
with the preserved Gruvbox theme. Post-restore HTTPS returned 200, no failed
system/user units were reported, and PipeWire/WirePlumber were active. Snapper
created snapshot 2 successfully. Provisioning passed with `ok=183 changed=0
failed=0`, including the boot-contract audits and installed configuration checks.
The candidate checkout remained clean at `ef74191`.

A machine-local `local.lua` override set inner gaps to 8 and reloaded without
config errors. Another provisioning run passed `ok=183 changed=0 failed=0`;
the live option remained 8, the selected theme remained Gruvbox, and the tracked
checkout remained clean. The desktop-menu Getting started action opened the
offline guide visibly in Ghostty. Audio opened Pavucontrol with the VM's audio
device, Network opened nmtui without changing the connection, and Display settings
opened the Hyprmon installation guide when that optional tool was absent.
Diagnostics and update-review subsequently failed on the second VM as recorded below.
Bluetooth hardware acceptance remains pending.

Additional live theme checks passed on 2026-11-03: applied Gruvbox Dark; unchanged
sync and preview both reported `changed=false`. A temporary Waybar template rule
made the clock red. Preview reported `changed=true` without switching the active
generation; apply switched generations and the red clock was visibly confirmed.
The original template was restored, synchronized, and the next preview reported
`changed=false`. Hyprland reported no config errors and the guest checkout was
clean afterward. The fixture was not committed to the candidate.

A second-person walkthrough remains unaccepted. A true
newer-kernel transition has not been exercised. Hardware, work accounts, meetings,
VPN/VM networking and independent backups remain separate workstation gates.

Installed versions include Linux 7.2.14, Limine 12.9.6, Hyprland 0.57.0,
Matugen 4.2.0, Hyprpaper 0.8.5, Hyprlock 0.9.7, Waybar 0.15.0 and Ghostty 1.4.0.
Package evidence is saved inside the guest under
`~/.local/state/hexen/rehearsal/`. Host-side operational evidence is ignored by Git.

Guest-agent/SSH access was used on live media, then a serial getty was started
after normal installed-account login for test observation. These were test
transport steps, not installer repairs; no remote-access packages were added.

A second VM, `hexen-fuzzel-ef74191-20261103`, has been created for the clean Fuzzel
path: UEFI, Secure Boot disabled, 2 CPUs, 4 GiB RAM and a new blank 64 GiB disk.
It uses the same verified Arch ISO. The public `ef74191` archive downloaded and
the interactive base install completed without errors or mirror repair, using
the synthetic `fuzzeluser` account. LUKS2/Btrfs, Limine 12.9.6 and Linux 7.2.14
were verified before reboot. Encrypted installed-disk boot was exercised next;
ordinary account login and Fuzzel first-boot provisioning then passed. Initial
Ansible apply: `ok=178 changed=47 failed=0`; rerun: `ok=172 changed=0 failed=0`.
Fuzzel 1.15.0-2 is installed; Walker and Elephant packages/binaries and their
build directory are absent. The configured launcher is `fuzzel`.

After provisioning, another encrypted reboot reached SDDM and normal graphical
authentication entered managed Hyprland with Waybar. Super+Space opened Fuzzel,
Firefox search found the desktop entry, and Enter launched Firefox visibly.
Health passed after graphical login, no system/user units were failed, HTTPS
returned 200, Hyprland reported no config errors, and theme sync preview reported
`changed=false` for Tokyo Night. The checkout remained clean at `ef74191`.
The Walker/recovery VM remains intact. A serial getty was enabled on the second
VM solely for persistent rehearsal observation.

## Blocking finding: graphical command lookup

On the unchanged Fuzzel candidate, Super+Alt+Space → Diagnostics opens Ghostty
but displays `bash: line 1: hexen: command not found`. Review updates opens
Ghostty with `Requested executable not found`. Both were observed directly.

The graphical Ghostty process and user systemd manager have a PATH that omits
`~/.local/bin`; the deployed `hexen` symlink exists and points at this checkout.
Provisioning adds that directory only in `.bashrc`, which interactive terminals
read but these direct/noninteractive menu commands do not. Reproducing the
graphical PATH in a noninteractive Bash fails `command -v hexen`; the explicit
`$HOME/.local/bin/hexen --help` succeeds under that same PATH. Running
`hexen doctor` from the interactive serial shell succeeds and reports the clean
candidate. This explains why earlier health and CLI checks did not catch the
menu failures. Relevant source: `config/bin/hexen-desktop` lines 183–184 and
`ansible/roles/desktop/tasks/main.yml` Bash initialization block.

Recommended correction: make desktop helper invocations resolve the deployed
Hexen command explicitly, and test the menu commands with a PATH that excludes
`~/.local/bin`. Audit graphical-session environment setup for other user helpers.
Retest both menu actions after normal graphical login on a new candidate commit;
do not count a VM-local PATH workaround as acceptance of `ef74191`. No candidate
implementation was changed during this rehearsal. This finding prevents full
workstation acceptance of the candidate.
