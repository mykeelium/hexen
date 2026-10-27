-- Repository-owned Omarchy/LazyVim startup, pinned by lazy-lock.json.
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
local lock = vim.json.decode(table.concat(vim.fn.readfile(vim.fn.stdpath("config") .. "/lazy-lock.json"), "\n"))
if not vim.uv.fs_stat(lazypath) then
  local clone = vim.fn.system({ "git", "clone", "--filter=blob:none", "https://github.com/folke/lazy.nvim.git", lazypath })
  if vim.v.shell_error ~= 0 then error("lazy.nvim clone failed: " .. clone) end
end
local current = vim.fn.system({ "git", "-C", lazypath, "rev-parse", "HEAD" }):gsub("%s+$", "")
if current ~= lock["lazy.nvim"].commit then
  local checkout = vim.fn.system({ "git", "-C", lazypath, "checkout", "--detach", lock["lazy.nvim"].commit })
  if vim.v.shell_error ~= 0 then error("lazy.nvim checkout failed: " .. checkout) end
end
vim.opt.rtp:prepend(lazypath)

require("lazy").setup({
  spec = {
    { "LazyVim/LazyVim", import = "lazyvim.plugins" },
    { import = "plugins" }, -- Omarchy themes and repository-local customizations
    { import = "machine.lazy" }, -- retained Base/Numen/Arcana features
  },
  defaults = { lazy = false, version = false },
  install = { colorscheme = { "gruvbox", "tokyonight", "habamax" } },
  checker = { enabled = true, notify = false },
  change_detection = { notify = false },
  performance = { rtp = { disabled_plugins = { "gzip", "tarPlugin", "tohtml", "tutor", "zipPlugin" } } },
})
