-- Run with the deployed owner configuration, after :Lazy restore.
assert(vim.v.errmsg == '', vim.v.errmsg)
local plugins = require('lazy.core.config').plugins
for _, name in ipairs({'nvim-dap', 'nvim-dap-ui', 'telescope.nvim', 'oil.nvim', 'snacks.nvim', 'nvim-treesitter'}) do
  assert(plugins[name], 'Missing merged feature: ' .. name)
end
assert(vim.fn.exists(':DapKeys') == 2, 'Base debugging key help missing')
assert(vim.wait(2000, function() return require('which-key.config').loaded end), 'which-key did not finish startup')
vim.api.nvim_exec_autocmds('LspAttach', { group = 'user_lsp_attach', buffer = 0, data = { client_id = 0 } })
vim.wait(250, function() return vim.fn.maparg('<leader>li', 'n') ~= '' end)
assert(vim.fn.maparg('<leader>li', 'n') ~= '', 'Numen LSP implementations key missing')
assert(vim.g.python3_host_prog == vim.fn.exepath('python3'), 'Python provider is machine-specific')
assert(require('oil').get_current_dir, 'Oil did not load')
assert(require('dap').listeners, 'DAP did not load')
vim.bo.filetype = 'lua'
assert(vim.treesitter.highlighter.active[vim.api.nvim_get_current_buf()], 'Lua syntax highlighting did not start')
local settings = vim.lsp.config.lua_ls.settings
assert(settings and settings.Lua and settings.Lua.diagnostics, 'Custom Lua LSP settings were not applied')
for _, language in ipairs({'c', 'c_sharp', 'lua', 'go', 'gosum', 'gomod', 'vim', 'vimdoc', 'elixir', 'javascript', 'html', 'python', 'typescript'}) do
  local ok, loaded = pcall(vim.treesitter.language.add, language)
  assert(ok and loaded, 'Configured parser missing: ' .. language)
end
for _, tool in ipairs({'lua-language-server', 'OmniSharp', 'gopls', 'basedpyright', 'ruff'}) do
  assert(vim.fn.executable(vim.fn.stdpath('data') .. '/mason/bin/' .. tool) == 1, 'Language tool missing: ' .. tool)
end
assert(vim.fn.executable('dlv') == 1, 'Go debugger missing')
print('Owner Neovim configuration startup and merged features passed')
