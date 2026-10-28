# Theme Builder Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Let users create reproducible, wallpaper-derived theme packs through an interactive terminal builder available from the desktop launcher.

**Architecture:** Extend the repository-owned `hexen-theme` Python CLI with a guided `create` subcommand. It stages a pack under `config/themes`, copies the wallpaper into the pack, validates it by rendering through existing Matugen templates, then atomically installs it and optionally calls the existing apply path. Add a launcher entry that runs the command in Ghostty and manage its symlink through the desktop Ansible role.

**Tech Stack:** Python 3 standard library, Matugen, Ghostty, Ansible desktop role, freedesktop `.desktop` entry.

**Spec:** `docs/superpowers/specs/2026-10-27-theme-builder-design.md`

## Global Constraints

- Keep theme pack data in the repository; generated user config remains in XDG state.
- Do not overwrite an existing theme pack or unmanaged user application entry.
- Do not add runtime packages; Python, Matugen, and Ghostty are already installed by the desktop role.
- Store the wallpaper inside its pack and reference it with a pack-relative path.
- Keep theme creation and application in the existing `hexen-theme` command.

## Review Focus

- Names that normalize to an empty or unsafe slug must be rejected before writing.
- Wallpaper paths with spaces or quotes must be copied safely to a simple pack-local filename.
- Unsupported/corrupt images or Matugen failures must not leave partial theme directories.
- Existing slug collisions must refuse cleanly without modifying the existing pack.
- Cancelling or declining apply must preserve a valid newly created pack and leave active theme unchanged.

---

### Task 1: Guided CLI and launcher installation

**Files:**
- Modify: `config/bin/hexen-theme`
- Create: `config/applications/hexen-theme-builder.desktop`
- Modify: `ansible/roles/desktop/tasks/main.yml`
- Modify: `ansible/roles/desktop/tasks/preflight.yml`
- Modify: `config/themes/README.md`
- Modify: `docs/desktop.md`

**Interfaces:**
- Add CLI command `hexen-theme create`.
- Add `create_theme_interactive() -> None` and small prompt/slug helpers in `config/bin/hexen-theme`.
- Desktop entry starts `ghostty -e ~/.local/bin/hexen-theme create` through the existing managed user shell.
- Ansible links the desktop entry from the repository and refuses to replace unmanaged entries.

- [x] Add the interactive prompt and safe staging flow to the existing CLI; use Matugen render validation before atomically renaming the staged pack, then offer to apply it.
- [x] Add the desktop application entry and matching preflight/link tasks.
- [x] Document the builder command, pack location, wallpaper copying, and apply behavior.
- [x] Manually inspect CLI help, compile the Python script, parse the desktop entry, inspect Ansible/YAML syntax, and run `git diff --check`.
