vim.keymap.set('n', '<Esc>', '<Cmd>nohlsearch<CR>', { desc = 'Clear search highlight' })
vim.keymap.set('n', '<leader>e', function()
  local ok, files = pcall(require, 'mini.files')
  if not ok then
    vim.cmd('Lexplore')
    return
  end
  local path = vim.api.nvim_buf_get_name(0)
  if vim.bo.buftype ~= '' or path == '' or vim.fn.filereadable(path) == 0 then
    path = vim.fn.getcwd()
  end
  files.open(path)
end, { desc = 'Open file explorer' })
