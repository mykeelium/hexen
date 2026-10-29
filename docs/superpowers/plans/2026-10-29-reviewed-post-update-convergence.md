# Reviewed Post-Update Convergence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (inline). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Offer reviewed Ansible convergence after a successful Hexen package update.

**Architecture:** Add an opt-in review mode to `install/provision.sh` that performs the existing dependency and syntax checks, runs Ansible in check/diff mode, then asks separately before the real playbook. `hexen update` offers this only after package diagnostics and successful migrations; VM network behavior requires explicit `--vm`. Save post-convergence package and failed-unit records in the existing recovery checkpoint.

**Tech Stack:** Bash provisioner, Python CLI, Ansible.

**Spec:** `docs/operations-roadmap.md`, “Complete remaining updater orchestration.”

## Global Constraints

- Do not run the updater, provisioner, or playbook on the host or VM during implementation.
- A declined preview must not apply configuration.
- Ansible check mode is advisory; command tasks that are not check-mode aware may be skipped. State this before confirmation and in the docs.
- Existing initial provisioning behavior remains unchanged.
- Do not restart or reboot automatically; keep source-specific application updates separate.
- Do not add or run tests unless requested; use syntax/help/diff checks only.

## Review Focus

- Provisioner cancellation after preview must exit distinctly from an applied run.
- `--vm` must flow consistently to preview and apply.
- Migration pending/failure must skip convergence.
- Convergence failure must be recorded without erasing successful package-update diagnostics.
- Post-convergence package and failed-unit records must reflect the resulting state.

### Task 1: Add provisioner review mode

**Files:**
- Modify `install/provision.sh`

- [x] Add `--review`, run check-mode with diff after syntax validation, explain check-mode limits, ask separately before real apply, and return a distinct status on decline.
- [x] Keep ordinary `install/provision.sh` behavior unchanged.

### Task 2: Offer convergence from `hexen update`

**Files:**
- Modify `config/bin/hexen`
- Modify `docs/machine-profiles.md`
- Modify `docs/operations-roadmap.md`

- [x] Add update `--vm`, offer review only after successful package work/migrations, record post-convergence package and failed-unit manifests, and report apply/decline/failure clearly.
- [x] Document that manual application sources remain separate and no reboot is automatic. Ansible may start/reload services, which the run transcript captures.
- [x] Mark only the Ansible convergence slice complete; keep other updater orchestration and VM acceptance open.

### Verification

- [x] `bash -n install/provision.sh`
- [x] Python AST parse for `config/bin/hexen`
- [x] Inspect provisioner and CLI help without running convergence
- [x] `git diff --check`
