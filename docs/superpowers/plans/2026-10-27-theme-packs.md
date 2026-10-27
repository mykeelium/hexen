# Named desktop theme packs Implementation Plan

> **For agentic workers:** Use the approved design in the linked spec. Implement each task in order and keep the shared interfaces below stable.

**Goal:** Let the user create and switch named desktop themes with wallpaper-derived or curated colors using Matugen and Hyprpaper.

**Architecture:** Theme packs live under `config/themes/<slug>/`. `hexen-theme` validates a pack, stages Matugen output under the user's state directory, atomically selects it, sets the wallpaper, and refreshes desktop apps. Shared configs import generated fragments and keep layout and behavior common to all themes.

**Tech Stack:** Bash launcher integration, Python 3 (`tomllib`, `json`, `pathlib`) for manifest/state handling, Matugen, Hyprpaper, existing Hyprland Lua and desktop apps.

**Spec:** `docs/superpowers/specs/2026-10-27-theme-packs-design.md`

## Global Constraints

- Install `matugen` and `hyprpaper` from signed Arch `extra` packages.
- Store generated output and active-theme state outside the repository.
- Do not overwrite user-owned application configuration or write generated files into repository-owned config directories.
- Keep Neovim's colorscheme independently selectable.
- Do not fetch themes or run arbitrary theme hooks.
- Preserve Tokyo Night as the initial palette and do not add personal wallpaper images without the owner's choice.

## Review Focus

- Malformed manifests or invalid slugs must be rejected before filesystem writes.
- Paths in theme packs must not escape the pack or the generated state directory.
- Matugen or wallpaper-application failure must leave the previously active theme selected.
- A missing/invalid wallpaper must not prevent applying a wallpaper-free curated palette.
- Theme activation must work with either selected launcher and with multiple monitor outputs.

---

## File map

- `ansible/roles/desktop/defaults/main.yml`: add the two official packages.
- `config/themes/`: starter theme pack, shared Matugen templates, and pack documentation.
- `config/bin/hexen-theme`: theme discovery, validation, rendering, activation, wallpaper, and CLI/menu interface.
- `config/bin/hexen-desktop`: expose the theme selector through the existing desktop menu.
- `config/{hypr,waybar,ghostty,mako,fuzzel,walker}`: import the active generated theme fragments.
- `ansible/roles/desktop/tasks/main.yml`: link the command into the desktop user's `~/.local/bin`.
- `docs/desktop.md`, `docs/app-sources.md`: describe the installed packages and user workflow.

## Task 1: Theme package and shared palette contract

**Files:**

- Modify: `ansible/roles/desktop/defaults/main.yml`
- Create: `config/themes/tokyo-night/theme.toml`
- Create: `config/themes/tokyo-night/palette.json`
- Create: `config/themes/templates/{hyprland.lua,waybar.css,ghostty.conf,mako.conf,fuzzel.ini,walker.css,hyprlock.conf,hyprpaper.conf}`
- Create: `config/themes/README.md`

**Interfaces:**

- A pack manifest has a lower-case hyphenated slug directory, display `name`, `mode` (`dark` or `light`), Matugen `type`, optional `wallpaper`, and wallpaper `fit_mode` (`cover`, `contain`, `fill`, or `tile`). Relative wallpaper paths must resolve inside the pack; an absolute path is an explicit reference to a user-owned image outside the repo.
- A pack may provide a curated `palette.json` with semantic fields used by all templates. When `wallpaper` is present, Matugen derives a palette from that image; otherwise the curated palette is rendered directly.
- Template inputs and output filenames form the stable app-fragment API consumed by Task 3.

- [ ] Add `matugen` and `hyprpaper` to the official desktop package list.
- [ ] Define the Tokyo Night palette from current values without adding a wallpaper image.
- [ ] Write one app fragment template per supported consumer, using a shared set of semantic color fields.
- [ ] Document how a user copies the starter pack, edits its manifest/palette, and optionally adds a wallpaper.
- [ ] Confirm every template consumes only fields provided by the curated palette or Matugen output.

## Task 2: Theme command and safe activation

**Files:**

- Create: `config/bin/hexen-theme`
- Modify: `ansible/roles/desktop/tasks/main.yml`

**Interfaces:**

- `hexen-theme list` prints pack slugs and display names.
- `hexen-theme current` prints the selected slug or reports no selected theme.
- `hexen-theme apply <slug>` validates, renders to a unique staging directory below `${XDG_STATE_HOME:-$HOME/.local/state}/hexen/themes/`, then switches a `current` symlink atomically.
- `hexen-theme` (no arguments) opens a menu using the selected Fuzzel or Walker backend and applies the selected pack.
- Errors go to stderr with nonzero exit status; the current symlink changes only after all rendering and path checks succeed.

- [ ] Implement strict slug/manifest/path validation with Python standard-library TOML and JSON parsers; reject relative paths that resolve outside the pack while allowing explicit absolute user wallpaper paths.
- [ ] Build the Matugen config at runtime so generated app fragments target the staging directory rather than the repo or active state.
- [ ] Support image-based generation and curated-palette rendering through Matugen's template mode.
- [ ] Add the interactive selector using the existing `~/.config/hexen/launcher` value; keep explicit CLI commands usable without a graphical session.
- [ ] Link the executable to `~/.local/bin/hexen-theme` through the desktop role.

## Task 3: Wallpaper and application integration

**Files:**

- Modify: `config/hypr/hyprland.lua`
- Create: `config/hypr/hyprpaper.conf`
- Modify: `config/hypr/theme.lua`
- Modify: `config/waybar/style.css`
- Modify: `config/ghostty/config.ghostty`
- Modify: `config/mako/config`
- Modify: `config/fuzzel/fuzzel.ini`
- Modify: `config/walker/themes/hexen/style.css`
- Modify: `config/hypr/hyprlock.conf`
- Modify: `config/bin/hexen-theme`
- Modify: `config/bin/hexen-desktop`

**Interfaces:**

- App configs include `~/.local/state/hexen/themes/current/<fragment>`; no include writes through the repo's config symlinks.
- Hyprpaper starts with the Hyprland user session and loads its generated config fragment at startup. Applying a pack with a wallpaper changes the live wallpaper; a pack without one retains the plain background.
- `hexen-desktop`'s existing menu includes `Themes` and launches `hexen-theme`.

- [ ] Replace duplicated app color literals with generated-fragment imports while retaining current spacing, fonts, opacity, and component layout.
- [ ] Start Hyprpaper from the desktop session and use the current pack's generated wallpaper configuration for login restore.
- [ ] On successful apply, change the wallpaper, reload Hyprland and Waybar, refresh Mako/Walker where supported, and leave Ghostty to pick up colors on its next window.
- [ ] Keep a wallpaper-free Tokyo Night selection visually equivalent to today's fixed palette.
- [ ] Add `Themes` to the existing Hexen menu without taking over a current Omarchy binding.

## Task 4: Provisioning and user documentation

**Files:**

- Modify: `docs/desktop.md`
- Modify: `docs/app-sources.md`
- Modify: `config/themes/README.md`

- [ ] Explain `hexen-theme`, the manifest fields, where to place wallpaper images, and how to add/switch a pack.
- [ ] Record that Matugen and Hyprpaper are signed official-repository packages.
- [ ] Document that Neovim themes remain independent and that generated files live under the user's state directory.
- [ ] Describe recovery behavior if a pack cannot be rendered and how to select Tokyo Night from the CLI.

## Final review

- Review all supported app includes and reload behavior against the installed app versions.
- Confirm no generated files or wallpaper assets are written into the repository during use.
- Compare the starter Tokyo Night fragment colors against the existing application values.
- Review shell quoting, path validation, and symlink activation in `hexen-theme`.
