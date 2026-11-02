-- Installed explicitly by tools/install-mini-files.py, never at startup.
local ok, files = pcall(require, 'mini.files')
if not ok then
  vim.schedule(function()
    vim.notify('mini.files is not installed; Space e uses Netrw.', vim.log.levels.WARN)
  end)
  return
end

files.setup({
  content = {
    -- No icon provider, Git integration or extra metadata queries.
    prefix = function() return '', '' end,
  },
  options = {
    permanent_delete = false,
    use_as_default_explorer = true,
  },
  windows = {
    max_number = 3,
    preview = false,
    width_focus = 35,
    width_nofocus = 20,
  },
})
