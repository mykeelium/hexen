# Desktop theme packs

Each directory in this folder is a named theme pack. `tokyo-night/` is the
starter pack and preserves the current palette without including a wallpaper.
`catppuccin-mocha/` is a second curated pack with a warmer background and
lavender/pink accents for comparing theme switching.
`catppuccin-latte/` is a light pack with a high-contrast palette that makes
switching behavior easy to see. `nord/` adds cool blue-gray colors,
`gruvbox-dark/` adds warm retro colors, and `everforest-dark/` adds muted
forest greens. The three dark packs are curated palettes and work without a
wallpaper.

To create a theme, copy the starter directory to a lowercase hyphenated name,
edit `theme.toml`, then either edit `palette.json` or add an image and set its
path in the manifest. A wallpaper takes precedence over `palette.json`; omit the
`palette` field if the pack has no curated palette. Wallpaper paths may be
relative to the pack directory or absolute paths to a local image. Relative
paths cannot escape the pack.
Paths may contain spaces, but cannot contain commas, line breaks, or Hyprland
config metacharacters (`#`, `$`, backslash, or quote).

For wallpaper-derived colors, `mode` can be `dark` or `light` and `type`
selects one of Matugen's supported schemes, such as `scheme-tonal-spot`,
`scheme-content`, or `scheme-fidelity`. `fit_mode` accepts `cover`, `contain`,
`fill`, or `tile` and requires a wallpaper. A custom palette uses Matugen's JSON color format
(`colors.<name>.<mode>.color`). Use the semantic colors in the starter palette
as a guide; its `terminal_0` through `terminal_15` entries preserve the full
curated Ghostty palette. Shared templates in `templates/` translate those roles
into each app's configuration format. Wallpaper-derived Ghostty colors use the
semantic Matugen colors because there is no hand-curated ANSI palette for an
image.

Use `hexen-theme` to choose a pack, `hexen-theme list` to browse packs,
`hexen-theme current` to see the active one, `hexen-theme apply <slug>` to
apply one from a terminal, or `hexen-theme create` to build a wallpaper-based
pack interactively. The builder copies the selected image into the new pack,
asks for a name, mode, Matugen scheme, and wallpaper fit, validates the image
through Matugen, and offers to apply the pack. It refuses to overwrite an
existing pack. The **Create Theme** launcher opens the same builder in Ghostty.
The builder does not modify Git state; review and commit the new directory if
you want the wallpaper and pack included in the reproducible setup.
Generated app fragments and active
theme state are stored under `${XDG_STATE_HOME:-~/.local/state}/hexen/themes`,
never in this repo. When provisioned, `~/.config/hexen/state-home` takes
precedence over `XDG_STATE_HOME` so desktop-launched helpers use the same
directory. The Ansible role uses `desktop_xdg_state_home` for initial
provisioning and exports the same directory in its managed Bash setup. App
configs read through the stable
`~/.config/hexen/theme` link, which follows the active generated theme. The
`current` symlink is switched only after validation and rendering complete. A
failed render leaves the previously selected theme active. Neovim's colorscheme
remains independently selectable. Theme changes reload the running Ghostty
user service when it is available, alongside the other desktop refreshes.
