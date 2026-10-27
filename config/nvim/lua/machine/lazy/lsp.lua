-- Extend LazyVim's native LSP configuration without replacing its setup.
-- Mason auto-install stays disabled per server; setup.lua installs tools explicitly.
return {
  {
    "neovim/nvim-lspconfig",
    opts = function(_, opts)
      opts.servers = opts.servers or {}
      opts.servers.lua_ls = { mason = false, settings = { Lua = { runtime = { version = "LuaJIT" }, diagnostics = { globals = { "vim", "love" } }, workspace = { library = { vim.env.VIMRUNTIME } } } } }
      opts.servers.omnisharp = { mason = false, enable_roslyn_analyzers = true, enable_import_completion = true, organize_imports_on_format = true, enable_decompilation_support = true, filetypes = { "cs", "vb", "csproj", "sln", "slnx", "props", "csx", "targets", "tproj", "slngen", "fproj" } }
      opts.servers.gopls = { mason = false, settings = { gopls = { analyses = { unusedparams = true, shadow = true }, staticcheck = true, gofumpt = true } } }
      opts.servers.basedpyright = { mason = false, settings = { basedpyright = { analysis = { autoSearchPath = true, useLibraryCodeForTypes = true } } } }
      opts.servers.ruff = { mason = false }
    end,
  },
  { "j-hui/fidget.nvim", opts = {} },
  { "mason-org/mason.nvim", opts = function(_, opts) opts.ensure_installed = {} end },
  { "mason-org/mason-lspconfig.nvim", opts = function(_, opts) opts.ensure_installed = {} end },
  { import = "lazyvim.plugins.extras.coding.nvim-cmp" },
}
