-- Keep native settings independent from optional extensions.
vim.g.mapleader = ' '
vim.g.maplocalleader = ' '

require('config.options')
require('config.autocmds')
require('config.mini')
require('config.keymaps')
