local which_key = require "which-key"
local builtin = require('telescope.builtin')

local function git_root()
  local root = vim.fn.systemlist("git rev-parse --show-toplevel")[1]
  return root and root ~= "" and root or nil
end

local function project_root()
  local git_root = vim.fn.systemlist("git rev-parse --show-toplevel")[1]
  if git_root and git_root ~= "" then
    return git_root
  end
  return vim.loop.cwd()
end

-- Guard Snacks once
local ok, Snacks = pcall(require, "snacks")
if not ok then
  return
end

vim.api.nvim_create_autocmd('LspAttach', {
  group = vim.api.nvim_create_augroup('user_lsp_attach', { clear = true }),
  callback = function(event)
    local opts = { buffer = event.buf }

    local mappings = {
      { "g",  group = "Go" },
      { "gd", vim.lsp.buf.definition, desc = "Go to definition" },
      { "K",  vim.lsp.buf.hover,      desc = "Show hover information" },

      -- Diagnostics (non-leader)
      {
        "gl",
        function()
          vim.diagnostic.open_float()
        end,
        desc = "Open diagnostic float",
      },
      {
        "[d",
        function()
          vim.diagnostic.goto_prev()
          vim.diagnostic.open_float()
        end,
        desc = "Previous diagnostic",
      },
      {
        "]d",
        function()
          vim.diagnostic.goto_next()
          vim.diagnostic.open_float()
        end,
        desc = "Next diagnostic",
      },

      -- LSP group (anchor prefix)
      { "<leader>l",  group = "LSP / Diagnostics" },

      { "<leader>la", vim.lsp.buf.code_action,      desc = "Code action" },
      { "<leader>lr", vim.lsp.buf.references,       desc = "References" },
      { "<leader>ln", vim.lsp.buf.rename,           desc = "Rename" },
      { "<leader>lw", vim.lsp.buf.workspace_symbol, desc = "Workspace symbol" },
      { "<leader>li", vim.lsp.buf.implementation,   desc = "Implementations" },

      {
        "<leader>ld",
        function()
          vim.diagnostic.open_float()
        end,
        desc = "Line diagnostics",
      },

      {
        "<leader>ll",
        function()
          vim.diagnostic.setloclist()
        end,
        desc = "Diagnostics → loclist",
      },

      {
        "<leader>lq",
        function()
          vim.diagnostic.setqflist()
        end,
        desc = "Diagnostics → quickfix",
      },
      -- { "<leader>ca", vim.lsp.buf.code_action,  desc = "Code Action" },
      -- { "[d",         vim.diagnostic.goto_next, desc = "Go to next diagnostic" },
      -- { "]d",         vim.diagnostic.goto_prev, desc = "Go to previous diagnostic" },
    }

    which_key.add(mappings, opts)

    -- vim.keymap.set('n', 'gd', function() vim.lsp.buf.definition() end, opts)
    -- vim.keymap.set('n', 'K', function() vim.lsp.buf.hover() end, opts)
    -- vim.keymap.set('n', '<leader>vws', function() vim.lsp.buf.workspace_symbol() end, opts)
    -- vim.keymap.set('n', '<leader>vd', function() vim.diagnostic.open_float() end, opts)
    -- vim.keymap.set('n', '[d', function() vim.diagnostic.goto_next() end, opts)
    -- vim.keymap.set('n', ']d', function() vim.diagnostic.goto_prev() end, opts)
    -- vim.keymap.set('n', '<leader>lca', function() vim.lsp.buf.code_action() end, opts)
    -- vim.keymap.set('n', '<leader>lrr', function() vim.lsp.buf.references() end, opts)
    -- vim.keymap.set('n', '<leader>lrn', function() vim.lsp.buf.rename() end, opts)
    -- vim.keymap.set('i', '<C-h>', function() vim.lsp.buf.signature_help() end, opts)

    -- https://www.mitchellhanberg.com/modern-format-on-save-in-neovim/
    vim.api.nvim_create_autocmd("BufWritePre", {
      buffer = event.buf,
      callback = function()
        vim.lsp.buf.format { async = false, id = event.data.client_id }
      end

    })
  end,
})

local non_lsp_mappings = {
  { "<leader>p", "\"_dP",                                                desc = "Paste without overwrite" },
  { "<leader>/", "<Plug>(comment_toggle_linewise_current)",              desc = "Toggle comment" },
  { "<leader>s", [[:%s/\<<C-r><C-w>\>/<C-r><C-w>/gI<Left><Left><Left>]], desc = "Search and replace word under cursor" },
  { "<leader>t", ":Today<CR>",                                           desc = "Open today's note" },
  { "J",         "mzJ`z",                                                desc = "Join lines and keep cursor position" },
  { "<C-d>",     "<C-d>zz",                                              desc = "Half page down and center" },
  { "<C-u>",     "<C-u>zz",                                              desc = "Half page up and center" },
  { "n",         "nzzzv",                                                desc = "Next search result and center" },
  { "N",         "Nzzzv",                                                desc = "Previous search result and center" },
  { "Q",         "<nop>",                                                desc = "Disable Ex mode" },
}

which_key.add(non_lsp_mappings)

local function get_dap()
  local ok, dap = pcall(require, "dap")
  if not ok then
    vim.notify("nvim-dap is not available", vim.log.levels.WARN)
    return nil
  end
  return dap
end

local function get_dapui()
  local ok, dapui = pcall(require, "dapui")
  if not ok then
    vim.notify("nvim-dap-ui is not available", vim.log.levels.WARN)
    return nil
  end
  return dapui
end

local dap_mappings = {
  { "<leader>d",  group = "Debug" },
  { "<F5>",       function() local dap = get_dap(); if dap then dap.continue() end end,        desc = "DAP Continue" },
  { "<F10>",      function() local dap = get_dap(); if dap then dap.step_over() end end,       desc = "DAP Step Over" },
  { "<F11>",      function() local dap = get_dap(); if dap then dap.step_into() end end,       desc = "DAP Step Into" },
  { "<F12>",      function() local dap = get_dap(); if dap then dap.step_out() end end,        desc = "DAP Step Out" },
  { "<leader>dc", function() local dap = get_dap(); if dap then dap.continue() end end,        desc = "DAP Continue" },
  { "<leader>dn", function() local dap = get_dap(); if dap then dap.step_over() end end,       desc = "DAP Step Over" },
  { "<leader>di", function() local dap = get_dap(); if dap then dap.step_into() end end,       desc = "DAP Step Into" },
  { "<leader>do", function() local dap = get_dap(); if dap then dap.step_out() end end,        desc = "DAP Step Out" },
  { "<leader>db", function() local dap = get_dap(); if dap then dap.toggle_breakpoint() end end, desc = "DAP Toggle Breakpoint" },
  {
    "<leader>dB",
    function()
      local dap = get_dap()
      if dap then
        dap.set_breakpoint(vim.fn.input("Breakpoint condition: "))
      end
    end,
    desc = "DAP Conditional Breakpoint",
  },
  { "<leader>dC", function() local dap = get_dap(); if dap then dap.run_to_cursor() end end,   desc = "DAP Run To Cursor" },
  { "<leader>dr", function() local dap = get_dap(); if dap then dap.repl.open() end end,       desc = "DAP REPL" },
  { "<leader>dl", function() local dap = get_dap(); if dap then dap.run_last() end end,        desc = "DAP Run Last" },
  { "<leader>dq", function() local dap = get_dap(); if dap then dap.terminate() end end,       desc = "DAP Terminate" },
  { "<leader>dx", function() local dap = get_dap(); if dap then dap.disconnect() end end,      desc = "DAP Disconnect" },
  {
    "<leader>du",
    function()
      local dapui = get_dapui()
      if dapui then
        dapui.toggle()
      end
    end,
    desc = "DAP UI Toggle",
  },
}

which_key.add(dap_mappings)

local function show_dap_keys()
  local lines = {
    "DAP Keys",
    "",
    "Function keys:",
    "F5  Continue",
    "F10 Step Over",
    "F11 Step Into",
    "F12 Step Out",
    "",
    "Leader keys:",
    "<leader>dc Continue",
    "<leader>dn Step Over",
    "<leader>di Step Into",
    "<leader>do Step Out",
    "<leader>db Toggle Breakpoint",
    "<leader>dB Conditional Breakpoint",
    "<leader>dC Run To Cursor",
    "<leader>dr REPL",
    "<leader>dl Run Last",
    "<leader>dq Terminate",
    "<leader>dx Disconnect",
    "<leader>du UI Toggle",
  }

  local buf = vim.api.nvim_create_buf(false, true)
  vim.api.nvim_buf_set_lines(buf, 0, -1, false, lines)
  vim.api.nvim_set_option_value("bufhidden", "wipe", { buf = buf })
  vim.api.nvim_set_option_value("modifiable", false, { buf = buf })

  local width = 0
  for _, line in ipairs(lines) do
    width = math.max(width, #line)
  end

  local height = #lines
  local win = vim.api.nvim_open_win(buf, true, {
    relative = "editor",
    width = width + 2,
    height = height,
    row = 2,
    col = 2,
    style = "minimal",
    border = "rounded",
  })

  vim.keymap.set("n", "q", function()
    if vim.api.nvim_win_is_valid(win) then
      vim.api.nvim_win_close(win, true)
    end
  end, { buffer = buf, silent = true, nowait = true })
end

vim.api.nvim_create_user_command("DapKeys", show_dap_keys, {})

which_key.add({
  { "<leader>d?", show_dap_keys, desc = "DAP Key Cheatsheet" },
})

-- vim.keymap.set("n", "<leader>e", vim.cmd.Ex)
-- vim.keymap.set("n", "J", "mzJ`z")       -- Keep cursor in same position on line join
-- vim.keymap.set("n", "<C-d>", "<C-d>zz") -- Keep cursor in middle on half page jump down
-- vim.keymap.set("n", "<C-u>", "<C-u>zz") -- Keep cursor in middle on half page jump down
-- vim.keymap.set("n", "n", "nzzzv")       -- Keep searched term in middle
-- vim.keymap.set("n", "N", "Nzzzv")       -- Keep reverse searched term in middle
-- vim.keymap.set("n", "Q", "<nop>")       --- Just undo capital Q support
-- vim.keymap.set("n", "<leader>/", "<Plug>(comment_toggle_linewise_current)")
-- vim.keymap.set("n", "<leader>s", [[:%s/\<<C-r><C-w>\>/<C-r><C-w>/gI<Left><Left><Left>]])
-- vim.keymap.set("n", "<leader>t", ":Today<CR>")

-- Telescope Commands

local telescope_mappings = {
  { "<leader>f",  group = "Find + Floating" },
  { "<leader>fF", builtin.find_files,       desc = "Telescope: find files" },
  { "<leader>fG", builtin.git_files,        desc = "Telescope: find git files" },
  { "<leader>fL", builtin.live_grep,        desc = "Telescope: live grep" },
}

which_key.add(telescope_mappings)

-- Register the semicolon mapping separately as it doesn't use the leader prefix
which_key.add({
  { ";", builtin.buffers, desc = "Find buffers" },
})

-- vim.keymap.set('n', '<leader>ff', builtin.find_files, {})
-- vim.keymap.set('n', '<leader>fg', builtin.git_files, {})
-- vim.keymap.set('n', '<leader>fl', builtin.live_grep, {})
-- vim.keymap.set('n', ';', builtin.buffers, {})



-- Use move command while highlighted to move text
-- vim.keymap.set("v", "J", ":m '>+1<CR>gv=gv")
-- vim.keymap.set("v", "K", ":m '<-2<CR>gv=gv")

-- vim.keymap.set("v", "<leader>/", "<Plug>(comment_toggle_linewise_visual)")

local visual_mappings = {
  { "J",         ":m '>+1<CR>gv=gv",                       desc = "Move selection down" },
  { "K",         ":m '<-2<CR>gv=gv",                       desc = "Move selection up" },
  { "<leader>/", "<Plug>(comment_toggle_linewise_visual)", desc = "Toggle comment" },
}

which_key.add(visual_mappings, { mode = "v" })

--- Don't overwrite pastes in visual mode
-- vim.keymap.set("x", "<leader>p", "\"_dP")


-- Format command
-- vim.keymap.set("n", "<leader>f", function()
-- vim.lsp.buf.format()
-- end)

-- insert commands
vim.keymap.set('i', '<Right>', '<Right>', { noremap = true }) -- Make the right arrow behave normally in insert mode

local git_mappings = {
  { "<leader>g",  group = "Git" },

  { "<leader>gR", function() Snacks.lazygit({ cwd = git_root() }) end, desc = "LazyGit (Root Dir)" },
  {
    "<leader>gG",
    function()
      Snacks.lazygit()
    end,
    desc = "LazyGit (cwd)",
    cond = function()
      return vim.fn.executable("lazygit") == 1
    end,
  },

  -- Git logs / history
  {
    "<leader>gL",
    function()
      Snacks.picker.git_log()
    end,
    desc = "Git Log (cwd)",
  },

  {
    "<leader>gl",
    function()
      Snacks.picker.git_log({ cwd = git_root() })
    end,
    desc = "Git Log (Root Dir)",
  },

  {
    "<leader>gb",
    function()
      Snacks.picker.git_log_line()
    end,
    desc = "Git Blame Line",
  },

  {
    "<leader>gf",
    function()
      Snacks.picker.git_log_file()
    end,
    desc = "Git Current File History",
  },

  -- Git browse
  {
    "<leader>gB",
    function()
      Snacks.gitbrowse()
    end,
    desc = "Git Browse (open)",
    mode = { "n", "x" },
  },

  {
    "<leader>gY",
    function()
      Snacks.gitbrowse({
        open = function(url)
          vim.fn.setreg("+", url)
        end,
        notify = false,
      })
    end,
    desc = "Git Browse (copy)",
    mode = { "n", "x" },
  },
}

which_key.add(git_mappings)

local terminal_mappings = {
  {
    "<leader>fT",
    function()
      Snacks.terminal()
    end,
    desc = "Terminal (cwd)",
  },

  {
    "<leader>ft",
    function()
      Snacks.terminal(nil, { cwd = project_root() })
    end,
    desc = "Terminal (Root Dir)",
  },

  {
    "<C-/>",
    function()
      Snacks.terminal(nil, { cwd = project_root() })
    end,
    desc = "Terminal (Root Dir)",
    mode = { "n", "t" },
  },

  {
    "<C-_>",
    function()
      Snacks.terminal(nil, { cwd = project_root() })
    end,
    desc = "which_key_ignore",
    mode = { "n", "t" },
  },
}

which_key.add(terminal_mappings)
