-- LazyVim's default picker is Snacks; preserve Telescope as an additional picker.
return { "nvim-telescope/telescope.nvim", dependencies = { "nvim-lua/plenary.nvim" }, opts = { defaults = { file_ignore_patterns = { "node_modules" } } } }
