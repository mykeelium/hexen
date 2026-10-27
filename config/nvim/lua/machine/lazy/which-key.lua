return {
  "folke/which-key.nvim",
  opts = {
    plugins = { marks = false, registers = false, spelling = { enabled = true, suggestions = 20 }, presets = { operators = false, motions = false, text_objects = false, windows = false, nav = false, z = false, g = false } },
    win = { padding = { 2, 2 }, wo = { winblend = 0 } },
    layout = { height = { min = 4, max = 25 }, width = { min = 20, max = 50 }, spacing = 3, align = "left" },
    show_help = true, show_keys = true, disable = { buftypes = {}, filetypes = { "TelescopePrompt" } },
  },
}
