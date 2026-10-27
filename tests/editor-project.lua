-- User-local smoke test: no external project, account, or third-party modules.
local directory = vim.fn.tempname()
vim.fn.mkdir(directory, 'p')
vim.fn.writefile({ 'module example.invalid/hexen-smoke', '', 'go 1.27' }, directory .. '/go.mod')
vim.fn.writefile({ 'package main', '', 'func main() {', '  answer := 42', '  _ = answer', '}' }, directory .. '/main.go')
local dap = require('dap')
local original_directory = vim.fn.getcwd()
local ok, err = pcall(function()
  vim.cmd.cd(directory)
  vim.cmd.edit(directory .. '/main.go')
  local buffer = vim.api.nvim_get_current_buf()
  assert(vim.wait(30000, function()
    local client = vim.lsp.get_clients({ bufnr = buffer, name = 'gopls' })[1]
    return client and client.initialized
  end, 100), 'gopls did not attach to the temporary Go module')
  local client = vim.lsp.get_clients({ bufnr = buffer, name = 'gopls' })[1]
  local response = client:request_sync('textDocument/hover', {
    textDocument = { uri = vim.uri_from_bufnr(buffer) },
    position = { line = 3, character = 4 },
  }, 15000, buffer)
  assert(response and not response.err and response.result and response.result.contents,
    'gopls did not return hover information for the local variable')
  print('Go language-server attach and hover passed')

  local stopped = false
  dap.listeners.after.event_stopped['hexen-smoke'] = function() stopped = true end
  dap.run({ type = 'go', name = 'Hexen smoke', request = 'launch',
    program = directory, mode = 'debug', stopOnEntry = true })
  assert(vim.wait(30000, function() return stopped end, 100),
    'Delve did not launch and stop the temporary Go program')
  print('Go debugger launch and stop-on-entry passed')
end)
dap.listeners.after.event_stopped['hexen-smoke'] = nil
dap.terminate()
vim.wait(5000, function() return dap.session() == nil end, 100)
vim.cmd.cd(original_directory)
vim.cmd('silent! bwipeout!')
vim.fn.delete(directory, 'rf')
assert(ok, err)
