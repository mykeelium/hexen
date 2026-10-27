-- Extend LazyVim's Treesitter setup with the union of Base/Numen/Arcana parsers.
return {
  {
    "nvim-treesitter/nvim-treesitter",
    opts = function(_, opts)
      opts.ensure_installed = opts.ensure_installed or {}
      vim.list_extend(opts.ensure_installed, require("config.tools").parsers)
    end,
  },
}
