# Source Checks and Service Review Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans (inline). Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Report local state for separately managed applications and provide an explicit post-update service restart review.

**Architecture:** Add a no-network source inventory to `hexen update --check` and the update checkpoint. Verify LocalSend against its tracked digest, report installed local versions/presence for separately owned apps, and clearly state that upstream freshness is not checked. Install Arch's `archlinux-contrib` and offer its `checkservices -P` command after updates; it skips `pacdiff` and prompts for service restarts.

**Tech Stack:** Python standard library, Arch packages, `checkservices`.

**Spec:** `docs/operations-roadmap.md`, updater orchestration item.

## Global Constraints

- Source checks are read-only and do not contact application upstreams.
- Never infer upstream freshness from an installed local version.
- `checkservices` is a separate opt-in action; it asks before service restarts and skips `pacdiff`.
- Do not run checks, service review, package update, or Ansible on the host/VM during implementation.
- No tests are added or run unless requested.

## Review Focus

- Missing, unsafe, or mismatched LocalSend paths are reported without execution.
- Missing utilities produce an unavailable status rather than aborting the update report.
- Service review is prompted separately, logged, and followed by a final failed-unit snapshot.
- Manual app/source freshness remains visibly owner-operated.

### Task 1: Add source-state report and service restart review

**Files:**
- Modify `config/bin/hexen`
- Modify `ansible/group_vars/all/packages.yml`
- Modify `docs/maintenance.md`
- Modify `docs/machine-profiles.md`
- Modify `docs/app-sources.md`
- Modify `docs/operations-roadmap.md`

- [x] Add LocalSend digest verification and local inventory output for Flatpak, manually installed packages, Hyprmon, and Neovim pins.
- [x] Add a separate `checkservices -P` prompt, status log, and final failed-unit record; include `archlinux-contrib` in the base package set.
- [x] Document limitations, service prompts, and remaining VM acceptance.

### Verification

- [x] Python AST parse for `config/bin/hexen`.
- [x] Bash syntax check for `install/provision.sh`.
- [x] `hexen update --help` and `install/provision.sh --help` only.
- [x] `git diff --check`.
