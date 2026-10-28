-- Repository-owned Omarchy/LazyVim startup, pinned by lazy-lock.json.
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
local lock_lines = vim.fn.readfile(vim.fn.stdpath("config") .. "/lazy-lock.json")
local lock = vim.json.decode(table.concat(lock_lines, "\n"))
-- lazy.nvim rewrites its working lock during incremental installs. Keep the
-- reviewed file immutable and constrain even specs discovered in later rounds.
local state_dir = vim.fn.stdpath("state") .. "/hexen"
vim.fn.mkdir(state_dir, "p")
local working_lock = state_dir .. "/lazy-lock.json"
vim.fn.writefile(lock_lines, working_lock)
local spec = {
  { "LazyVim/LazyVim", import = "lazyvim.plugins" },
  { import = "plugins" },
  { import = "machine.lazy" },
}
for name, pin in pairs(lock) do
  spec[#spec + 1] = { name, commit = pin.commit, optional = true }
end
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
  spec = spec,
  lockfile = working_lock,
  defaults = { lazy = false, version = false },
  install = { colorscheme = { "gruvbox", "tokyonight", "habamax" } },
  checker = { enabled = true, notify = false },
  change_detection = { notify = false },
  performance = { rtp = { disabled_plugins = { "gzip", "tarPlugin", "tohtml", "tutor", "zipPlugin" } } },
})
