local group = vim.api.nvim_create_augroup('BghEditing', { clear = true })

-- Restore a valid last cursor position; never jump in commit messages.
vim.api.nvim_create_autocmd('BufReadPost', {
  group = group,
  callback = function(event)
    if vim.bo[event.buf].buftype ~= '' then return end
    if vim.bo[event.buf].filetype == 'gitcommit' then return end
    if vim.fn.fnamemodify(event.file, ':t') == 'COMMIT_EDITMSG' then return end
    local position = vim.api.nvim_buf_get_mark(event.buf, '"')
    if position[1] > 1 and position[1] <= vim.api.nvim_buf_line_count(event.buf) then
      pcall(vim.api.nvim_win_set_cursor, 0, position)
    end
  end,
})
