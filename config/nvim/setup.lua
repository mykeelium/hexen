-- Explicit user-local language setup; run after :Lazy restore (see README).
local tools = require('config.tools')
local parsers = require('nvim-treesitter').install(tools.parsers)
if parsers then parsers:wait(240000) end
for _, language in ipairs(tools.parsers) do
  local loaded, err = vim.treesitter.language.add(language)
  assert(loaded, err or ('Parser installation failed: ' .. language))
end
local registry = require('mason-registry')
local refreshed, success = false, false
registry.refresh(function(ok) refreshed, success = true, ok end)
assert(vim.wait(60000, function() return refreshed end, 100) and success, 'Mason registry refresh failed')
for _, name in ipairs(tools.servers) do
  local package = registry.get_package(name)
  if not package:is_installed() and not package:is_installing() then package:install() end
end
local installed = vim.wait(240000, function()
  for _, name in ipairs(tools.servers) do
    local package = registry.get_package(name)
    if not package:is_installed() or package:is_installing() then return false end
  end
  return true
end, 200)
local missing = {}
for _, name in ipairs(tools.servers) do
  if not registry.get_package(name):is_installed() then table.insert(missing, name) end
end
assert(installed, 'Language tools not installed: ' .. table.concat(missing, ', '))
print('Configured parsers and language tools installed')
