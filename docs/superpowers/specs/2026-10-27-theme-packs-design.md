# Named desktop theme packs

## Intent

Make desktop appearance easy to create and switch as named, repository-owned
themes, with wallpaper-derived colors through Matugen and wallpaper display
through Hyprpaper. Keep the app configuration readable and shared instead of
copying full config directories for each theme. The user selected named packs
with Matugen and agreed that Neovim keeps its independently selectable
colorscheme in this first version.

## Current state

Tokyo Night colors are repeated as literal values in Hyprland, Waybar, Ghostty,
Mako, Fuzzel, Walker, and Hyprlock configuration. Hyprland keeps gaps and border
colors in `config/hypr/theme.lua`; there is no wallpaper package or wallpaper
startup path. Neovim has its own Omarchy-derived theme collection and currently
selects Gruvbox.

## Goals

- Install Matugen and Hyprpaper from signed Arch repositories.
- Add named theme packs under the repo's configuration tree. A pack should be
  straightforward to copy and edit, and support an optional wallpaper plus
  Matugen mode/scheme settings and a manual seed or palette override.
- Provide one documented `hexen-theme` interface to list, inspect, and apply a
  pack. With no pack name, offer a selection menu through the chosen Fuzzel or
  Walker launcher.
- Render shared semantic colors to app-specific fragments for Hyprland,
  Waybar, Ghostty, Mako, Fuzzel/Walker, and Hyprlock. Keep app structure and
  behavior in their shared repository configs.
- Set the chosen wallpaper with Hyprpaper and persist the active theme so the
  next session restores both wallpaper and generated colors.
- Keep generated output outside the repository and avoid overwriting user-owned
  application config. Make theme selection independent of wallpaper assets
  being committed when the pack references a local image path.
- Preserve Tokyo Night as the initial appearance and make adding a new pack
  possible by copying a documented starter pack and editing its manifest,
  image, and (when desired) color overrides.

## Non-goals

- Change Neovim's independent colorscheme system or force image-derived colors
  into Neovim.
- Import Omarchy's theme manager or install AUR theme tools.
- Random wallpaper rotation, online theme downloads, or arbitrary theme hooks.
- Rebuild app configuration or keybindings when a theme is selected.

## Approaches

1. **Named packs with shared templates (selected).** Each pack holds metadata,
   an optional image, and palette-generation choices. Shared Matugen templates
   map palette colors to semantic tokens and emit app fragments. A single
   command selects the pack, applies wallpaper, atomically updates generated
   output, and refreshes affected desktop processes. This balances editing and
   reuse, and keeps updates to app layout in one place.
2. **Full app-config bundles per pack.** Copy each app config into each theme
   and switch a current-theme symlink. This offers maximum per-theme freedom,
   but duplicates behavior/layout and makes package config updates harder to
   carry across themes.
3. **Always derive from the current wallpaper.** Run Matugen whenever a
   wallpaper is selected, without named packs or pack-level settings. This is
   the smallest interface, but makes manually curated themes and predictable
   switching harder.

## Proposed structure and behavior

- Keep shared token-to-app mappings and Matugen templates in one repository
  location; keep theme-specific metadata and optional assets under
  `config/themes/<slug>/`.
- A theme manifest names the theme and selects a local wallpaper (optional),
  dark/light mode, Matugen scheme, and any seed or custom palette inputs. Exact
  fields should follow Matugen's supported config and import interfaces.
- `hexen-theme list`, `current`, and `apply <slug>` are scriptable. Calling
  `hexen-theme` opens a Fuzzel/Walker selection menu. Applying a theme validates
  its manifest, image, and expected output paths before changing state; renders
  to a staging directory; switches the active generated theme atomically; sets
  the wallpaper; and reloads/restarts only applications that need it.
- App configs import generated fragments from a stable per-user state path.
  They remain symlinked to shared repo files as they are today. Generated
  files and active-theme state do not live in the clone.
- Hyprpaper starts with the Hyprland session. The active wallpaper is restored
  at login; wallpaper-free packs preserve the existing plain background.
- The starter `tokyo-night` pack preserves current colors and behavior. It may
  omit a wallpaper until the owner adds one. The README explains how to copy
  that pack, add a wallpaper, adjust its generation options, and preview/apply
  it.
- Palette changes affect Hyprland border colors, Waybar, Ghostty, Mako,
  Fuzzel/Walker, and Hyprlock. Existing fonts, layout, sizing, and component
  behavior remain shared unless an explicit shared theme token is added.
- Keep explicit CLI application available even if the launcher is unavailable;
  report failures without leaving a partially selected theme.

## Constraints and risks

- Config include/reload behavior differs among the apps. Implementations must
  use each app's supported include mechanism and refresh behavior rather than
  writing into symlinked repo directories.
- Hyprpaper and Matugen interfaces can change. Use current upstream docs and
  Arch package interfaces during implementation; the package names are
  `matugen` and `hyprpaper` in Arch `extra`.
- Some generated color combinations may have weak contrast. Keep the current
  dark palette as a stable initial pack, use semantic mappings, and document
  how to tune generation or overrides.
- Wallpaper assets can make the git clone large. Packs may reference an
  external user-owned image path instead of committing the image; the starter
  documentation should explain both choices.

## Builder decisions

- Select a safe atomic activation mechanism compatible with the existing
  symlinked configs and per-user state.
- Choose per-app generated-fragment includes and refresh commands.
- Define strict validation for pack slugs, manifest fields, file paths, and
  Matugen output paths.
- Do not include personal wallpaper assets in the repository without the
  owner's explicit choice.
