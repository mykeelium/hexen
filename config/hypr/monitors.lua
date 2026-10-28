-- Generated display rules belong to this machine, outside the linked repo.
local home = os.getenv('HOME')
local state = os.getenv('XDG_STATE_HOME') or (home .. '/.local/state')
local marker = io.open(home .. '/.config/hexen/state-home', 'r')
if marker then
  state = marker:read('*l') or ''
  marker:close()
end
if state:sub(1, 1) ~= '/' then error('Hexen state directory must be absolute') end
local path = state .. '/hexen/displays/hyprmon.lua'
local file = io.open(path, 'r')
if file then file:close(); dofile(path) end
