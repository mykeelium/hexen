# Work laptop installation checklist

Updated 2026-11-06. Target: Dell XPS 14 9440, replacing Mint with Hexen.
The owner is comfortable erasing the internal disk. This records installation
intent; no disk has been erased as part of these checks.

Drata is tracked separately. This checklist does not resolve that requirement.

Follow the [detailed wiped-disk-to-workstation runbook](work-laptop-install-runbook.md)
for the owner's chosen internal-install path. VPN testing must happen only on
the work laptop after installation. The owner accepts testing the actual desktop
stack after internal installation rather than requiring an external-disk trial.

## Current software evidence

Candidate: `8f6d3808f10616e71ba0bc949c19451405ff08c1`.

- [x] Local suite: 96 tests passed, no skips, using the documented dependencies
  and Unix socket access.
- [x] Ansible playbook syntax, Bash syntax and Git whitespace checks passed.
- [x] All three candidate CI jobs passed: onboarding, theme-sync and
  arch-interactive. [CI evidence](https://github.com/mykeelium/hexen/actions/runs/41706799223).
- [x] Anonymous candidate archive downloaded; all 250 regular files matched
  the Git commit byte-for-byte.

These checks establish source behavior, not physical hardware or work readiness.
If the candidate changes, repeat affected checks for the new exact revision.

## P0 — Before erasing Mint

1. [ ] **Recovery:** restore representative work files from an independent
   backup and compare them. Confirm whether the backup restores the whole Mint
   installation or only files. Keep usable recovery media and required
   credentials outside the laptop.
2. [ ] **Employer requirements:** confirm Arch is permitted, required endpoint
   tools are available, VPN support is viable, and whether Secure Boot is
   mandatory. This candidate requires Secure Boot disabled. Drata remains a
   separate open requirement.
3. [x] **Hardware inventory:** run the read-only checker on the actual laptop:
   `python3 install/hardware.py --profile xps-14-9440`. Confirm the expected
   Intel/NVIDIA GPUs, UEFI and disabled Secure Boot. Owner supplied a successful
   report on 2026-11-06; rerun from the live media before installation.
4. [ ] **Hardware acceptance after installation:** test the intended Arch,
   NVIDIA and Hyprland stack on the work XPS. Verify three independent 1920x1200
   displays, their ordering, KVM switching, USB-C reconnection, lid behavior,
   suspend/resume and lock/unlock. A text-mode ISO or VM cannot accept these.
5. [ ] **Representative work session:** after installation on the work XPS, test VPN and
   internal resources, Firefox, Slack notifications, a Zoom meeting with camera
   and microphone, monitor/window sharing, and build/test a real Go project.
6. [ ] **Essential peripherals:** verify Wi-Fi, headphones, speakers, Bluetooth,
   brightness and battery behavior. Prioritize devices needed for daily work.

## P1 — Finish candidate rehearsal before internal installation

1. [ ] **Exact-candidate desktop:** verify graphical Diagnostics and Review
   updates, encrypted boot and login, launcher/browser actions, and repeat
   provisioning. Earlier rehearsal records include older revisions.
2. [ ] **Update and rollback:** exercise a newer-kernel update/reboot and check
   the resulting system. Rehearse offline restoration using the matching root
   snapshot and EFI archive. A VM tests the workflow; the physical trial must
   establish kernel/GPU behavior on the XPS.
3. [ ] **Instruction walkthrough:** have another person follow the public
   instructions and record any assistance required.

## P2 — Installation day

1. [ ] Pin the tested full source revision for both installation stages. Have
   verified Arch media with Archinstall 4.5, network access, another computer
   and sufficient downtime available.
2. [ ] Reconfirm backup access, then disconnect backup disks and other storage
   that must not be erased.
3. [ ] Boot the Arch ISO in UEFI mode. Identify the internal disk by model,
   serial and capacity; record its actual device path. Do not reuse a VM path.
4. [ ] Deliberately remove the old partition layout/signatures on that selected
   disk from the live environment, after checking mounts and active mappings.
   Verify the disk now meets Hexen's blank-disk requirements before continuing.
5. [ ] Preview, then run the Hexen installer with `--hardware xps-14-9440`;
   add `--install` for the installation run. Review the disk and erase
   confirmation interactively.
6. [ ] After encrypted installed-disk boot, obtain the same source revision and
   run first boot with `--hardware xps-14-9440`, without `--vm`.
7. [ ] Reboot and repeat hardware, work-session and service checks before
   relying on the laptop for work. Complete the separate Drata gate.

## When disk preparation happens

The current **Hexen wrapper requires a blank disk before it launches
Archinstall**. It excludes disks with partitions, a partition table, a filesystem
signature or a mountpoint. The generated Archinstall configuration then creates
the new ESP and encrypted Btrfs layout.

You can do the preparatory removal during the same installation session, from
the Arch ISO shell immediately before running the Hexen wrapper. You do not
need to erase Mint from within Mint or before booting the ISO. You cannot defer
this preparation to the Archinstall menu reached through the current wrapper,
because its occupied-disk check runs first. Bypassing the wrapper would leave
the tested Hexen installation path.

Removing partition/filesystem metadata is destructive preparation, not a secure
erase of every old data block. A full-device overwrite is not required merely
to satisfy the installer's blank-disk check. Choose concrete preparation
commands only after inspecting the actual disk and its active mappings.

See [XPS installation](xps-14-9440.md), [candidate acceptance](candidate-acceptance.md),
[quickstart](quickstart.md) and [recovery](recovery.md) for the detailed procedures.
