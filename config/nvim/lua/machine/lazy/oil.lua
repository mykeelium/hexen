return {
  {
    "stevearc/oil.nvim",
    cmd = "Oil",
    opts = require("core.oil"),
    dependencies = { { "nvim-mini/mini.icons", opts = {} } },
    keys = { { "<leader>fo", "<cmd>Oil<cr>", desc = "Open Oil file explorer" } },
  },
}
