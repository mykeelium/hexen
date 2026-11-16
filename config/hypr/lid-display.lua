-- Remove the internal panel from the desktop while the lid is closed.
-- Unlike DPMS, disabling the output also evacuates its workspaces.
local function set_laptop_display(closed)
  hl.monitor({
    output = 'eDP-1',
    disabled = closed,
    mode = 'preferred',
    position = 'auto',
    scale = 'auto',
  })
end

hl.bind('switch:on:Lid Switch', function()
  set_laptop_display(true)
end, { locked = true })

hl.bind('switch:off:Lid Switch', function()
  set_laptop_display(false)
end, { locked = true })

-- Switch bindings only see transitions. Also handle login/config reload with
-- the lid already closed, using this machine's verified ACPI lid-state path.
local lid = io.open('/proc/acpi/button/lid/LID0/state', 'r')
if lid then
  local state = lid:read('*a')
  lid:close()
  set_laptop_display(state:match('closed') ~= nil)
end
