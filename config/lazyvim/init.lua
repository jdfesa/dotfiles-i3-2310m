vim.g.mapleader = " "
vim.g.maplocalleader = "\\"

-- Keep generated preferences outside the managed configuration.
vim.g.lazyvim_json = vim.fn.stdpath("state") .. "/lazyvim.json"
local setup = vim.env.BGH_LAZYVIM_SETUP == "1"
local lazypath = vim.fn.stdpath("data") .. "/lazy/lazy.nvim"
if not vim.uv.fs_stat(lazypath) then
  error("LazyVim is not provisioned. See the editor setup guide, or use nvim --clean.")
end
vim.opt.rtp:prepend(lazypath)

-- Also find the user-installed Tree-sitter CLI in non-login invocations.
local bin = vim.env.HOME .. "/.local/bin"
if not vim.tbl_contains(vim.split(vim.env.PATH or "", ":", { plain = true }), bin) then
  vim.env.PATH = bin .. ":" .. (vim.env.PATH or "")
end

require("lazy").setup({
  spec = {
    { "LazyVim/LazyVim", tag = "v16.0.2", import = "lazyvim.plugins" },
    -- Keep the base UI, parsers and completion. Provision language tools only on request.
    { "neovim/nvim-lspconfig", opts = { servers = { lua_ls = { enabled = false } } } },
    { "mason-org/mason.nvim", build = false, opts = function(_, opts)
      opts.ensure_installed = {}
    end },
  },
  defaults = { lazy = false, version = false },
  concurrency = 2,
  install = { missing = setup, colorscheme = { "tokyonight", "habamax" } },
  checker = { enabled = false },
  change_detection = { enabled = false },
})
