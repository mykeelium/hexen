# Interactive Package Update Review Implementation Plan

> **For agentic workers:** Use `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** Add a terminal-first, package-by-package review flow to `hexen update-monitor` that persists owner decisions and only hands off to the existing full-system update workflow after an explicit choice.

**Architecture:** Extract structured discovery data from the current Markdown/report flow. Keep review choices, evidence recording, and orchestration independent from the line-oriented terminal prompts so a richer TUI can reuse them later. Preserve the scheduled no-argument command and the existing update confirmation/checkpoint path.

**Tech Stack:** Python standard library, argparse, JSONL private evidence, existing `checkupdates` and Pacman workflows.

**Spec:** `docs/superpowers/specs/2026-10-29-interactive-update-review-design.md`

## Global Constraints

- No automatic package installation, privileged transaction, system database refresh, or snapshot during review.
- No partial package transaction; flags record intent only and the eventual transaction remains a full system upgrade.
- Keep the scheduled `hexen update-monitor` behavior unchanged.
- Keep decision records private, user-owned, and appended to the existing evidence stream.
- Do not add a TUI dependency in this implementation.
- Do not run or add tests unless the user requests testing; use static syntax and diff checks only.
- Work in the existing checkout because the owner previously requested direct source edits here and will make the final commit.

## Review Focus

- Stale, failed, offline, or empty discovery must never reach an update handoff.
- Noninteractive invocation must fail before prompting or recording package choices.
- Invalid input and interrupted review must preserve already-recorded decisions without starting an update.
- Every package decision must be associated with the discovery identity and exact versions/repository shown to the owner.
- Explicit handoff must still enter `command_update`, preserving that workflow's independent confirmations.

## Files

- Modify `config/bin/hexen`: structured discovery result, review state/prompt orchestration, evidence events, and argparse routing.
- Modify `docs/machine-profiles.md`: explain review command, package decision meanings, evidence location, and full-upgrade behavior.
- Modify `docs/app-sources.md`: list the package-by-package review route as the Arch update procedure.
- Modify `docs/operations-roadmap.md`: mark source implementation complete while retaining VM acceptance as open.
- Modify `docs/resume.md`: record implementation and the outstanding VM acceptance.

## Tasks

### Task 1: expose structured update discovery

**Files:** `config/bin/hexen`

- [x] Introduce typed discovery/package records containing check time, status, detail, report path, and each package's name, installed version, candidate version, and repository.
- [x] Refactor discovery/report generation so scheduled `hexen update-monitor` preserves its current report, evidence, notification, and exit behavior.
- [x] Provide a non-notifying discovery path for interactive review that writes the same private report and discovery event.
- [x] Static-check Python syntax and inspect the diff for unchanged no-argument routing.

### Task 2: implement terminal review and explicit handoff

**Files:** `config/bin/hexen`

- [x] Add `hexen update-monitor review`, requiring an interactive stdin and stdout before any prompts; preserve the existing `--vm` convergence choice as an optional review flag.
- [x] Refuse review on failed/stale/up-to-date discovery; show candidate versions, repository, Arch package page, and recipe-history links for available updates.
- [x] Keep decision handling independent from prompts; support `reviewed`, `wanted`, `follow-up`, and `undecided` states, appending each completed decision immediately with the discovery identity and package metadata.
- [x] Support safe interruption, summarize all package decisions, and record cancel or explicit full-update handoff.
- [x] On handoff call the existing `command_update()` path and retain its own confirmation, source review, checkpoint, and full `pacman -Syu` behavior.
- [x] Static-check Python syntax and inspect the CLI flow and evidence fields.

### Task 3: document and record roadmap status

**Files:** `docs/machine-profiles.md`, `docs/operations-roadmap.md`

- [x] Document how to run the review, what each decision means, where choices are recorded, and why choices cannot filter a Pacman transaction.
- [x] Mark the roadmap source implementation complete and explicitly leave VM acceptance open.
- [x] Run `git diff --check` and review the final scoped diff without staging or committing.
