# Beta readiness follow-up plan

**Goal:** give the owner an ordered, checkable backlog for releasing a usable
Hexen preview and then extending it to newcomers installing on hardware.

**Status:** planning only. No implementation or installation acceptance is
implied by this document. The owner will make the source changes; a future
agent must receive an explicit implementation request before doing so.

**Architecture:** retain the existing Archinstall adapter for base installation
and Ansible for installed-system configuration. Improve their handoff and user
experience incrementally. Hardware support and automatic cross-reboot handoff
are separate follow-up projects, not prerequisites for every preview release.

**Tech stack:** Bash, Python, Archinstall 4.5, Ansible, systemd, Hyprland Lua.

**References:** [guided installer design](../specs/2026-10-30-guided-archinstall-design.md),
[earlier preview work](2026-10-30-preview-readiness.md),
[release checklist](../../release-checklist.md),
[latest rehearsal](../../installer-preview-validation-2026-10-30.md), and
[workstation roadmap](../../operations-roadmap.md).

## Scope and constraints

- Proposed initial audience: disposable-VM testers. The owner has not yet
  selected a broader public support scope.
- Preserve x86_64 UEFI, a single blank disk of at least 40 GiB, LUKS2, Btrfs,
  Limine, explicit disk selection and interactive destructive confirmation.
- Preserve the exact Archinstall version check and in-memory credentials.
- Keep publication, repository visibility changes, tagging, disk operations,
  and changes to the development host outside this documentation task.
- Keep manual recipe/archive review and normal package signature verification.
- Do not claim hardware, account, update or recovery acceptance from unit tests.
- Keep passwords, tokens and Wi-Fi credentials out of handoff records and logs.

## Review focus

Verify these cases explicitly rather than relying on a successful default run:

1. A Fuzzel selection must neither build Walker nor fail health checks for it.
2. A non-US keyboard must behave consistently at installation, login and lock.
3. Cancelling a stage must not produce a setup-success message.
4. A normal shortcut customization must not block the supported update path.
5. A first-boot retry must explain its effects, including another full upgrade.

## Priority 0: prepare an honest, repeatable VM preview

### 1. Set the release boundary

**Files:** `README.md`, `docs/quickstart.md`, `docs/known-issues.md`,
`docs/release-checklist.md`.

- [ ] Choose the supported audience before describing the release as a beta.
- [ ] For the proposed VM preview, state the accepted VM environment, UEFI,
  Secure Boot setting, RAM, disk size, ISO and Archinstall requirements up front.
- [ ] State that dual boot, reinstalling occupied disks and physical hardware
  support remain outside that preview.
- [ ] Complete the existing source/privacy and third-party notice reviews.

**Done when:** a reader can tell whether their intended installation is
supported before downloading or running anything.

### 2. Make launcher selection consistent across setup

**Files:** `install/first-boot.sh`, `install/provision.sh`, `install/health.py`,
`tests/test_first_boot.py`, `tests/test_provision_cli.py`, `docs/quickstart.md`.

- [ ] Add regression coverage for Fuzzel setup without Walker installed and
  for Walker's existing package/provider requirements before changing behavior.
- [ ] Choose the launcher before installing launcher-specific dependencies.
- [ ] Pass that choice through provisioning without a conflicting second choice;
  retain an interactive choice for standalone provisioning.
- [ ] Have health checks inspect the configured launcher and require only its
  tools. Keep the selected launcher's runtime requirements intact.
- [ ] Distinguish cancellation from successful provisioning in the first-boot
  caller; an already provisioned system must not hide a cancelled rerun.
- [ ] Verify cancellation before prerequisites, cancellation at provisioning,
  and a failed Walker build do not print setup completion.
- [ ] Confirm the Arch interactive CI job passes on GitHub. It runs first-boot
  and provisioner tests as a regular user; the Ubuntu job skips those cases.
- [ ] Document that retries can run `pacman -Syu` again; do not call the current
  rerun behavior a checkpointed resume operation.

**Done when:** both launcher paths work on clean disposable systems, missing
dependencies identify the selected launcher, and cancellation ends clearly.

### 3. Resolve the keyboard-layout mismatch

**Files:** `install/archinstall/generate.py`, `config/hypr/hyprland.lua`,
`ansible/roles/desktop/tasks/main.yml`, `tests/test_archinstall_generator.py`,
`docs/quickstart.md`, `docs/known-issues.md`.

- [x] Scope the generated VM preview to US keyboard layout; stop offering other
  console choices and document the restriction. Archinstall's review menu still
  allows edits, so the quickstart tells users to keep US selected.
- [ ] For multi-layout support, define how console keymaps map to XKB layouts
  and variants; do not assume their names are interchangeable.
- [ ] Carry the selected desktop layout into machine-local configuration rather
  than changing the shared defaults for every installation.
- [ ] Add coverage that a supported non-US selection reaches desktop settings
  and unsupported mappings fail with a useful explanation.
- [ ] Rehearse console login, graphical login and lock/unlock with a supported
  non-US layout and a synthetic password containing layout-sensitive symbols.

**Done when:** the US-only path is accepted at console login, graphical login and
lock/unlock in the candidate VM. Support for additional layouts remains open.

### 4. Finish the release download and update instructions

**Files:** `docs/quickstart.md`, `install/archinstall/README.md`,
`docs/release-checklist.md`, release notes; inspect `config/bin/hexen` source
update behavior when deciding the installed checkout instructions.

- [ ] Freeze the candidate revision after the required fixes and documentation.
- [ ] Supply exact archive and installed-system checkout commands for that
  revision. Both stages must use the same accepted source.
- [ ] Supply the local branch/upstream instructions required by the current
  updater; choosing a detached tag alone skips source updates.
- [ ] Explain the long-term checkout location and why it must remain in place.
- [ ] Replace maintainer-facing placeholders in the quickstart with final user
  instructions. Verify the archive's extracted directory name.
- [ ] Once the owner authorizes publication, verify anonymous repository and
  archive access. Do not treat authenticated maintainer access as evidence.

**Done when:** someone without repository credentials can follow copyable
commands and obtain the accepted revision at both installation stages.

### 5. Accept the frozen candidate from the public instructions

**Files:** `docs/release-checklist.md`, `docs/installer-preview-validation-2026-10-30.md`,
`docs/known-issues.md`; add a new dated evidence record for the candidate run.

- [ ] Use a new disposable VM disk and a synthetic account different from the
  owner's. Use only the quickstart and its linked public instructions.
- [ ] Complete the final HTTPS mirror configuration without an undocumented
  manual repair; if repair is needed, document/fix it and repeat affected checks.
- [ ] Verify encrypted boot, first-boot setup, SDDM, managed Hyprland, selected
  launcher, normal/private browser launch, lock/unlock and working networking.
- [ ] Rerun provisioning with the same selections and explain unexpected changes.
- [ ] Exercise the documented full update/reboot and paired root/ESP recovery
  workflow. Record a real newer-kernel transition only if one was exercised;
  keep that limitation explicit if no newer kernel is available.
- [ ] Have a second person follow the quickstart and record where they hesitate.
- [ ] Record source commit, ISO hash, installer version, VM resources, results
  and limitations. Review logs before sharing; exclude credentials.
- [ ] If source changes after acceptance, test the changed paths again before
  calling the new revision accepted. Publish/tag only with owner authorization.

**Done when:** the release checklist cites evidence for the exact published
revision and all outstanding limitations are visible in the release notes.

## Priority 1: make the desktop comfortable for newcomers

### 6. Keep ordinary customization compatible with updates

**Files:** `config/bin/hexen-desktop`, `config/hypr/bindings.lua`,
`config/hypr/hyprland.lua`, `docs/desktop.md`, `docs/machine-profiles.md`,
`tests/test_desktop_helper.py`; inspect the dirty-checkout guard in `config/bin/hexen`.

- [ ] Make the normal keybinding/appearance editing actions open machine-local
  overrides; retain tracked files for deliberate shared project changes.
- [ ] Explain how to override a binding, reload, check errors and undo the edit.
- [ ] Cover menu targets with the existing helper tests.
- [ ] Verify one ordinary customization leaves tracked source clean, survives
  provisioning and remains compatible with the supported update workflow.

**Done when:** a user can personalize a shortcut without learning Git first.

### 7. Make essential settings and help discoverable

**Files:** `config/bin/hexen-desktop`, `docs/desktop.md`, `docs/quickstart.md`,
`ansible/roles/desktop/defaults/main.yml`, `tests/test_desktop_helper.py`.

- [ ] Add accessible entries for networking, audio, Bluetooth, shortcuts,
  updates, diagnostics and recovery/help using the existing tools where possible.
- [ ] Resolve the display-settings dependency: provide an accepted install path
  or give an actionable explanation when Hyprmon is absent.
- [ ] Add a small welcome/help view explaining Super, app launch, terminal,
  window closing, workspaces, lock, settings and where to report a problem.
- [ ] Include a TTY recovery route for graphical login failures.
- [ ] Verify the actions in a fresh desktop session without optional manual apps.

**Done when:** a newcomer can connect, launch apps, change basic settings and
find help without searching development notes.

## Priority 2: design broader installer support as separate projects

These are proposals to design before implementation. They extend the approved
installer scope and are not automatic requirements for the VM preview.

### 8. Hardware detection and an explicit support matrix

- [ ] Inventory VM type, CPU, GPU(s), storage, firmware mode, networking and
  laptop/display devices before installation; show findings and proposed support.
- [ ] Define and test driver/firmware policies for specific supported devices,
  including NVIDIA and hybrid-graphics cases. Stop clearly for unsupported cases.
- [ ] Detect VM mode by default, explain the selected mode and retain a validated
  override. Reuse that mode during later provisioning/update operations.
- [ ] Guide live-ISO network setup and installed-system reconnection without
  exposing Wi-Fi credentials in logs or handoff records.
- [ ] Publish a tested matrix covering boot, graphics, Wi-Fi, audio, Bluetooth,
  brightness, external displays and suspend/resume on each supported machine.

**Done when:** hardware support claims are backed by tests on named devices,
and unsupported hardware is identified before destructive operations.

### 9. A continuous experience across the reboot boundary

- [ ] Design a versioned, non-secret handoff containing source revision, selected
  mode, launcher and supported input settings; define ownership and validation.
- [ ] Preserve the accepted source on the installed system and provide an obvious
  first-login continuation command, avoiding a second arbitrary checkout.
- [ ] Define stage statuses, private log locations and safe retry rules. Keep
  destructive base installation separate from retryable desktop provisioning.
- [ ] Test interruption at each stage, a moved/missing checkout, a mismatched
  source revision and malformed handoff data. Never resume destructive work
  merely because a previous stage left a marker.

**Done when:** users can identify their current stage and continue safely after
an interruption without reconstructing the workflow themselves.

## Verification notes for the next session

Run focused checks for each changed component before the fresh-VM acceptance:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py'
bash -n install/first-boot.sh install/provision.sh install/archinstall/hexen-install.sh config/bin/hexen-desktop
git diff --check
```

The review session ran 51 Python tests: 37 passed and 14 screensaver tests failed
in a sandbox that denies Unix socket binding. A controller fixture independently
returned `Operation not permitted`. The 17 onboarding tests passed separately.
Rerun the screensaver suite in an environment with Unix socket access before
claiming the complete suite passes. None of these checks replaces install,
update, recovery or physical-hardware acceptance.

Start with tasks 1–5 for the proposed VM preview. Tasks 6–7 improve everyday
usability; tasks 8–9 need their own designs and implementation plans. The
[release checklist](../../release-checklist.md) remains the release decision
record; the [workstation roadmap](../../operations-roadmap.md) retains the
broader work-computer, account, backup and hardware gates.
