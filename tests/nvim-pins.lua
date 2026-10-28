-- Run after startup; unlike UI assertions this also works in headless mode.
local source = vim.json.decode(table.concat(
  vim.fn.readfile(vim.fn.stdpath('config') .. '/lazy-lock.json'), '\n'))
local checked = 0
for name, plugin in pairs(require('lazy.core.config').plugins) do
  if not plugin._.is_local then
    local pin = assert(source[name], 'Active plugin is missing a reviewed pin: ' .. name)
    assert(plugin.commit == pin.commit, 'Missing reviewed commit constraint: ' .. name)
    local result = vim.system({'git', '-C', plugin.dir, 'rev-parse', 'HEAD'}, {text = true}):wait()
    assert(result.code == 0, 'Cannot inspect installed plugin: ' .. name)
    assert(vim.trim(result.stdout) == pin.commit, 'Installed revision differs from reviewed pin: ' .. name)
    checked = checked + 1
  end
end
assert(checked > 0, 'No plugin revisions were checked')
print('Reviewed plugin constraints and installed revisions passed: ' .. checked)
