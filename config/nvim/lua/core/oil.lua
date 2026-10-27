return {
  columns = { "icon" },
  buf_options = { buflisted = false, bufhidden = "hide" },
  win_options = { wrap = false, signcolumn = "no", cursorcolumn = false, foldcolumn = "0", spell = false, list = false, conceallevel = 3, concealcursor = "n" },
  default_file_explorer = true, restore_win_options = true, skip_confirm_for_simple_edits = false, delete_to_trash = false, prompt_save_on_select_new_entry = true,
  keymaps = { ["g?"] = "actions.show_help", ["<CR>"] = "actions.select", ["<C-s>"] = "actions.select_vsplit", ["<C-h>"] = "actions.select_split", ["<C-t>"] = "actions.select_tab", ["<C-p>"] = "actions.preview", ["<C-c>"] = "actions.close", ["<C-l>"] = "actions.refresh", ["-"] = "actions.parent", ["_"] = "actions.open_cwd", ["`"] = "actions.cd", ["~"] = "actions.tcd", ["g."] = "actions.toggle_hidden" },
  use_default_keymaps = true,
  view_options = { show_hidden = true, is_hidden_file = function(name) return vim.startswith(name, ".") end, is_always_hidden = function() return false end },
  float = { padding = 2, border = "rounded", win_options = { winblend = 10 } },
}
