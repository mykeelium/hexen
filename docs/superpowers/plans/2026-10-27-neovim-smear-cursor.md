# Neovim Smear Cursor Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Enable a Neovide-inspired animated cursor in terminal Neovim.

**Architecture:** Use `sphamba/smear-cursor.nvim` through the existing Lazy.nvim import. Replace the mistaken Flash navigation plugin and preserve reproducibility with an exact lockfile pin and source inventory entry.

**Tech Stack:** Neovim Lua, Lazy.nvim, JSON lockfile, Markdown documentation.

**Spec:** The approved approach in the conversation: replace `flash.nvim` with `smear-cursor.nvim`, enable it on startup, pin its release, and document how to toggle it and its terminal-rendering limitation.

## Global Constraints

- Keep the active plugin specification in `config/nvim/lua/machine/lazy/`.
- Keep the lockfile commit and plugin source inventory synchronized.
- Do not change system packages or Ghostty configuration.
- Preserve all unrelated repository modifications.

## Review Focus

- Lazy import should discover and initialize the plugin without manual startup commands; confirm spec path and `opts` activation.
- Lockfile and source inventory must identify the same plugin revision; parse JSON and compare the commit.
- Documentation must not claim the animation affects shell cursor movement outside Neovim.

---

### Task 1: Replace Flash with the smear cursor plugin

**Files:**
- Delete: `config/nvim/lua/machine/lazy/flash.lua`
- Create: `config/nvim/lua/machine/lazy/smear_cursor.lua`
- Modify: `config/nvim/lazy-lock.json`
- Modify: `config/nvim/PLUGIN-SOURCES.md`
- Modify: `config/nvim/README.md`

**Interfaces:**
- Consumes: existing `machine.lazy` import and Lazy.nvim plugin spec conventions.
- Produces: `sphamba/smear-cursor.nvim` loaded by Lazy.nvim with default options and a lockfile commit matching the source inventory.

- [ ] **Step 1: Add the plugin spec and remove the Flash spec**

Use the canonical plugin repo and an `opts = {}` spec to initialize it with upstream defaults. Remove Flash's lock entry and add the exact selected release commit under the plugin's lockfile name.

- [ ] **Step 2: Update the source inventory and README**

Replace the Flash row with the smear-cursor source and revision. Replace the README's Flash mapping explanation with the terminal animation behavior, `:SmearCursorToggle`, and the known terminal rendering limitation.

- [ ] **Step 3: Verify static consistency**

Run `python3 -m json.tool config/nvim/lazy-lock.json`, `luac -p config/nvim/lua/machine/lazy/smear_cursor.lua`, and `git diff --check`. Confirm Flash is absent from active config, lockfile, inventory, and README, and the plugin pin matches in the lockfile and inventory.
