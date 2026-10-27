-- Union of the active Base/Numen/Arcana language support.
return {
  parsers = { 'c', 'c_sharp', 'lua', 'go', 'gosum', 'gomod', 'vim', 'vimdoc', 'elixir', 'javascript', 'html', 'python', 'typescript' },
  servers = { 'lua-language-server', 'omnisharp', 'gopls', 'basedpyright', 'ruff' },
}
