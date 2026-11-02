vim.opt.number = true
vim.opt.relativenumber = false
vim.opt.wrap = false
vim.opt.scrolloff = 4
vim.opt.ignorecase = true
vim.opt.smartcase = true
vim.opt.splitbelow = true
vim.opt.splitright = true
vim.opt.undofile = true
vim.opt.backupcopy = 'yes' -- Preserve symlinks when writing managed files.

-- Fallback only: runtime filetype indentation can override these values.
vim.opt.expandtab = true
vim.opt.tabstop = 4
vim.opt.shiftwidth = 4
vim.opt.softtabstop = 4

-- Native highlights, with no theme plugin or transparency.
vim.opt.termguicolors = true
vim.opt.background = 'dark'
local highlights = {
  Normal = { fg = '#cdd6f4', bg = '#1e1e2e' },
  NormalFloat = { fg = '#cdd6f4', bg = '#181825' },
  FloatBorder = { fg = '#6c7086', bg = '#181825' },
  LineNr = { fg = '#6c7086' },
  CursorLineNr = { fg = '#f9e2af', bold = false },
  StatusLine = { fg = '#cdd6f4', bg = '#313244' },
  StatusLineNC = { fg = '#a6adc8', bg = '#181825' },
  Comment = { fg = '#a6adc8', italic = false },
  Directory = { fg = '#89b4fa' },
  Visual = { bg = '#45475a' },
  Search = { fg = '#1e1e2e', bg = '#f9e2af' },
}
for group, attributes in pairs(highlights) do
  vim.api.nvim_set_hl(0, group, attributes)
end
