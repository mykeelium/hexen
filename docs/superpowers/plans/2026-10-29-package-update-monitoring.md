# Package Update Monitoring Implementation Plan

> **For agentic workers:** This plan is being executed inline by the current session; tasks use checkbox syntax for tracking.

**Goal:** Add daily, non-installing Arch update discovery with private review reports and auditable owner decisions.

**Architecture:** `hexen update-monitor` runs `checkupdates` against a dedicated per-user state database, writes timestamped private reports and evidence, and notifies through `notify-send` when available. A persistent systemd user timer invokes it. The existing interactive `hexen update` remains the only package installation path and records installed package deltas alongside its Pacman transcript.

**Tech Stack:** Python standard library, `checkupdates` from `pacman-contrib`, systemd user units, `notify-send` from `libnotify`.

**Spec:** `docs/operations-roadmap.md` package monitoring section.

## Global Constraints

- The daily job runs unprivileged and does not install packages or update the system Pacman sync database.
- Reports and work-monitoring evidence are user-private (`0700` directories, `0600` files).
- Failed/offline checks are reported as unknown, never “up to date.”
- Signature verification is recorded from Pacman's transaction; it is not represented as proof of benign source/build.
- Missing source/artifact evidence is explicitly “not compared.”
- Never invoke privileged updates from notifications.

## Review Focus

- `checkupdates` status 0 means updates, 2 means none, and other statuses mean failure.
- Empty, malformed, or unexpected package output must not be called current.
- Notification failure must not discard the report.
- Existing updater checkpoint data may be incomplete; package deltas must label unknowns.
- Non-Arch package sources remain outside this Pacman monitor's coverage.

## Files

- Modify `config/bin/hexen` for monitor CLI, private report/evidence, notification, and installed package delta capture.
- Create `config/systemd/user/hexen-update-monitor.service` and `.timer`.
- Modify desktop Ansible defaults/tasks to deploy and enable the user timer and ensure `pacman-contrib` and `libnotify` are installed.
- Modify `docs/machine-profiles.md`, `docs/app-sources.md`, and `docs/operations-roadmap.md` with user operation, limitations, employer-policy caveat, and acceptance status.

## Tasks

- [x] Add isolated daily `checkupdates` run, report generation, private evidence, and optional desktop notification.
- [x] Add systemd user service/timer and provisioner deployment/activation.
- [x] Record package manifest deltas and provenance links in update checkpoints; make artifact gaps explicit.
- [x] Document manual review and owner review/apply/decline records; keep VM and employer-policy acceptance open.

## Verification

Per user instruction, do not run tests, systemd jobs, Ansible, Pacman, or `checkupdates` on the host/VM. Python AST parsing and `git diff --check` passed. VM exercise and employer-policy acceptance remain open.
