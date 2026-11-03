# Candidate acceptance procedure

Use this procedure to evaluate a VM preview. Every checkbox starts open;
previous rehearsals are useful context, not acceptance of a new revision.

## Prepare a candidate

- [ ] Select and record a clean Git commit after reviewing the proposed fixes.
  Record the full commit with `git rev-parse HEAD`; `git status --short` must
  have no output. Do not call a moving branch an accepted revision.
- [ ] Record ISO filename, SHA-256, Archinstall version, VM name and resources.
  Preserve the current Archinstall 4.5 requirement; other versions need their
  own compatibility work.
- [ ] Use a new disposable VM with x86_64 UEFI, Secure Boot disabled, a US
  keyboard, at least 4 GiB RAM (8 GiB recommended), and a blank disk of at
  least 40 GiB. Attach no physical host disks.
- [ ] Choose a synthetic account and interactively entered passwords. Keep
  passwords, tokens and recovery codes out of evidence and screenshots.
- [ ] Supply candidate-specific archive and installed checkout commands before
  testing. Both stages must obtain the same full source commit. Verify a local
  branch and its upstream are configured for the documented update workflow.
  Public-download acceptance requires anonymous access; authenticated access
  does not prove it. Publication is a separate owner action.

## Check source behavior

From the candidate checkout, run:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'
bash -n install/first-boot.sh install/provision.sh install/archinstall/hexen-install.sh config/bin/hexen-desktop
git diff --check
```

- [ ] Record counts, skips, failures and the execution environment. Run the
  interactive first-boot/provisioner cases as a regular Arch user with PTY
  access, including the Arch interactive CI job. Run the dedicated theme-sync
  CI job so its real Ansible task integration case is exercised. A skipped case
  is not passed.
- [ ] Run screensaver tests where Unix socket binding is allowed. If sandbox
  restrictions prevent them, record the limitation instead of accepting them.

## Rehearse installation

Follow [the quickstart](quickstart.md) and its linked instructions. Do not
silently repair the guest using private maintainer notes.

- [ ] Preview the plan; confirm the selected blank disk, encryption and account.
- [ ] Complete installation with the final HTTPS mirror configuration. If a
  repair is necessary, record it, fix the relevant instructions/source, and
  repeat the affected path on a fresh disk.
- [ ] Boot the installed disk, unlock LUKS and log into the synthetic account.
  Perform the linked boot checks and confirm networking.
- [ ] Obtain the same candidate commit in its permanent checkout location.
- [ ] Save the installed package manifest (`pacman -Q`) and renderer version
  (`matugen --version` after desktop setup) with the evidence. A Git commit pins
  Hexen's source, not the changing Arch repository package versions.
- [ ] Complete first boot as the regular user. Test Walker and Fuzzel on
  separate clean installations so installed Walker packages cannot mask a
  Fuzzel dependency failure.
- [ ] Verify cancellation before prerequisites, cancellation at provisioning,
  and a failed Walker build do not report setup completion. Retrying may run
  a full Arch upgrade again; record what changed.

## Accept the desktop

- [ ] Reboot into SDDM and enter the managed Hyprland session.
- [ ] Check selected launcher search; for Walker, also check calculation and
  web search. Check normal/private browser shortcuts.
- [ ] Verify US input at console login, graphical login and lock/unlock.
- [ ] Open the offline welcome guide, networking, audio, Bluetooth, diagnostics
  and update review from the Hexen menu. Record unavailable VM devices.
- [ ] Check the absent-Hyprmon guide, or its installed display-settings action.
- [ ] Save a harmless local customization, reload and check configuration errors.
  Verify tracked Git source remains clean, then verify the customization remains
  after provisioning. Do not equate opening an editor with saving a valid edit.
- [ ] Rerun provisioning with the same selections. Record and explain any changes;
  unexpected changes or failures leave the repeatability gate open.
- [ ] Select a nondefault theme and verify provisioning preserves that choice.
  Rehearse a reviewed theme-template change: preview reports it without changing
  the active generation, apply updates generated output, and the next unchanged
  run reports no theme change. Check the affected desktop apps after reload or
  login. Keep this fixture change outside the accepted candidate unless it is
  intended to ship, and record which source was used for each check.

## Accept updates and recovery

Use the existing [maintenance](maintenance.md),
[update workflow](machine-profiles.md#checking-update-status) and
[recovery](recovery.md) instructions inside the disposable guest.

- [ ] Record the source revision and installed/running kernel before updating.
- [ ] Create and verify the paired root snapshot and EFI archive, review and
  perform the full update, then reboot and check encrypted boot, networking,
  audio, desktop and failed services.
- [ ] Record the installed/running kernel afterward. If no newer kernel was
  available, keep the newer-kernel transition gate open.
- [ ] Exercise offline recovery using the matching root snapshot and EFI archive.
  Verify restored boot, retained home files, Snapper and provisioning afterward.
- [ ] Have another person follow the candidate instructions and record where
  they need help.

Do not improvise disk or rollback commands from this checklist; use the linked
procedures with the guest's actual layout. VM acceptance does not establish
hardware compatibility, work-account access or independent backup restoration.

## Record the result

Create a dated evidence note containing:

```text
Candidate full commit:
ISO filename / SHA-256:
Archinstall version:
VM firmware / CPUs / RAM / disk:
Launcher:
Source tests: passed / failed / skipped
Installation and mirror result:
Desktop and repeat-provisioning result:
Kernel before / after / running after reboot:
Recovery pair and restore result:
Known failures and untested cases:
Decision: accepted VM preview / blocked
```

Evidence must name the tested revision and distinguish observed behavior from
source review. Review logs before sharing. If fixes change the candidate,
record its new revision and rerun affected checks before release. Tagging and
publication remain separate from completing this procedure.
