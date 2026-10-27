# Neovim configuration

This configuration uses the complete user-facing Omarchy Neovim setup as its foundation: LazyVim defaults, Omarchy’s theme collection and theme reload hook, no-news settings, and disabled animated scrolling. Its source was copied from the locally installed `omarchy-nvim 2026.4.23-1` package. Only configuration source and the Apache-2.0 license are included; package caches, plugin checkouts, Mason payloads, and Omarchy-managed system files are not copied.

The selected theme is a checked-in snapshot of the host’s current Omarchy theme, Gruvbox. Change `lua/plugins/theme.lua` to select another included theme. The hot-reload hook operates only on this repository-owned config.

## Owner profile merge

The Base source snapshot is `mykeelium/nvim-config` commit `e45b8249bfb152c20f9089100ca95f00eeef5ba1`; the Omarchy config snapshot is from local package `omarchy-nvim 2026.4.23-1`. The `machine.lazy` specs retain the union of active Base, Numen, and Arcana features. Base remains the foundation; Numen’s `<leader>li` implementation mapping is included, and where Arcana adds no unique active feature there is nothing additional to overlay. LazyVim now supplies standard editor functions (including `<leader>qq` to quit all, bufferline, Lualine, Gitsigns, native LSP integration, and the default picker). The previous configuration remains layered on with completion via nvim-cmp, Telescope, Oil, Snacks integrations, DAP and Go debugging, colorizer, Today notes, Treesitter parser additions, custom diagnostics and options, and the owner keymaps.

Omarchy/LazyVim defaults retain their standard keybindings. Additional Telescope actions use `<leader>fF`, `<leader>fG`, and `<leader>fL`; Oil uses `<leader>fo`. The Omarchy `<leader>e` file picker and `<leader>gg` LazyGit bindings are left intact. The Numen LSP implementation action remains `<leader>li`.

The generic Omarchy starter example is intentionally not imported: it includes sample plugins, language servers, and automatic package installs that are unrelated to this machine. The repository’s former starter example is likewise inert. `lazyvim.json` retains Omarchy’s enabled Neo-tree extra.

## Installation and updates

The desktop role links this directory to the selected user’s `~/.config/nvim`, refusing existing unmanaged configuration. Provisioning does not run plugin builds or language-tool downloads as root. Run as the target user with network access:

```sh
nvim --headless '+Lazy! restore' +qa
nvim --headless '+lua dofile(vim.fn.stdpath("config") .. "/setup.lua")' +qa
nvim
```

The combined lockfile contains 71 repositories and pins. Shared repositories use Omarchy’s package lock revision; Base-only repositories keep their imported Base revision. See [PLUGIN-SOURCES.md](PLUGIN-SOURCES.md). `setup.lua` is the explicit installer for the listed Treesitter parsers and five Mason tools. Mason’s automatic tool list is cleared so normal startup does not install language servers; tools are installed only when `setup.lua` is run. Treesitter follows LazyVim’s configured parser behavior.

Mason and parser artifacts are separately downloaded upstream and are not fixed by the plugin lockfile. Their versions and build sources should be reviewed when changing setup. Plugins can execute code as the desktop user.

Ghostty cursor shaders remain vendored locally; see [the shader notes](../ghostty/shaders/README.md). The current VM preserves its existing Neovim data directory while restoring this repository’s plugin pins.
