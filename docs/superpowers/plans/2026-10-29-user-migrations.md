# User Migration Runner Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an explicit, resumable, per-user runner for reviewed Hexen migrations, invoked only after a successful package transaction.

**Architecture:** Keep a versioned JSON manifest and numbered Python scripts in `install/migrations/`. Validate IDs, ordering, and script paths before execution. Run scripts as the logged-in user, serialize execution with a private lock, and atomically write a private completion marker only after success. `hexen migrate` runs pending migrations interactively; `hexen update` offers the same pending work after Pacman and package-state capture.

**Tech Stack:** Python standard library, JSON manifest, Python migration scripts.

**Spec:** `docs/operations-roadmap.md`, item “Add a migration mechanism before changing user data automatically.”

## Global Constraints

- Migrations are numbered, versioned with the repository, idempotent, resumable, logged, and run per user.
- No migration runs during the Pacman transaction or as root.
- Completion markers live in Hexen's per-user state directory and are written only after success.
- No concrete migration is added in this slice.
- No tests are added or run; this follows the workspace instruction unless the user asks for tests.

## Review Focus

- Invalid or unsafe manifest paths: reject before running any migration.
- Interrupted/failed migration: preserve earlier markers and leave the failed migration pending.
- Concurrent invocations: private lock permits only one runner.
- Marker write interruption: atomic replacement prevents partial completion records.
- User declines update-time migrations: keep package diagnostics, report pending work, and allow later `hexen migrate`.

### Task 1: Implement registry and runner

**Files:**
- Create `install/migrations/manifest.json`
- Modify `config/bin/hexen`

- [x] Add manifest loading and validation, private per-user state/lock handling, ordered resumable execution, private logs, and atomic completion markers.
- [x] Add interactive `hexen migrate`; no pending migrations should exit without mutation.

### Task 2: Integrate and document post-package execution

**Files:**
- Modify `config/bin/hexen`
- Modify `docs/machine-profiles.md`
- Modify `docs/operations-roadmap.md`
- Modify `docs/app-sources.md`

- [x] Offer pending migrations only after successful Pacman and package-state capture; refusal or migration failure must remain visible while post-update diagnostics still run.
- [x] Document the manifest contract, user-level state/log paths, retry behavior, and the absence of concrete migrations.
- [x] Mark the framework item complete while leaving VM acceptance and remaining updater orchestration open.

### Verification

- [x] Parse `config/bin/hexen` with Python's AST parser.
- [x] Inspect `hexen migrate --help` without invoking migrations.
- [x] Run `git diff --check`.
