-- Adapted from Omarchy 8e03151647ef210ce9e313180e642d3e58dbe9a6.
-- See docs/licenses/omarchy.txt and docs/desktop.md for parity/deviations.
-- This is the one place to edit keyboard shortcuts. Local overrides load last.
local d = hl.dsp
local function bind(key, description, action, options)
  options = options or {}
  options.description = description
  return hl.bind(key, action, options)
end
local function command(key, description, action, options)
  return bind(key, description, d.exec_cmd(action), options)
end
local helper = '"$HOME/.local/bin/hexen-desktop" '

-- App launch keys match Omarchy. Applications remain explicit package choices.
command('SUPER + Return', 'Terminal', 'ghostty')
command('SUPER + ALT + Return', 'Zellij', 'ghostty -e zellij attach --create Work')
command('SUPER + SHIFT + Return', 'Browser', helper .. 'browser')
command('SUPER + SHIFT + B', 'Browser', helper .. 'browser')
command('SUPER + SHIFT + ALT + B', 'Private browser', helper .. 'browser-private')
command('SUPER + SHIFT + F', 'File manager', 'nautilus --new-window')
command('SUPER + SHIFT + I', 'Bluetooth devices', 'ghostty --class=io.github.hexen.bluetui -e bluetui')
command('SUPER + SHIFT + N', 'Editor', 'ghostty nvim')
command('SUPER + SHIFT + O', 'Obsidian', 'obsidian')
command('SUPER + SHIFT + slash', 'Passwords', helper .. 'passwords')
command('SUPER + Space', 'Launch apps', helper .. 'launcher')
command('SUPER + ALT + Space', 'Hexen menu', helper .. 'menu')
command('SUPER + Escape', 'System menu', helper .. 'system-menu')
command('XF86PowerOff', 'System menu', helper .. 'system-menu', { locked = true })
command('SUPER + K', 'View/edit key bindings', 'ghostty nvim "$HOME/.config/hypr/bindings.lua"')
command('SUPER + SHIFT + Space', 'Toggle bar', 'pkill -SIGUSR1 -x waybar')
command('SUPER + CTRL + L', 'Lock', 'loginctl lock-session')
command('Print', 'Screenshot region to clipboard', helper .. 'screenshot')
command('SUPER + CTRL + V', 'Clipboard history', helper .. 'clipboard')
command('SUPER + comma', 'Dismiss notification', 'makoctl dismiss')
command('SUPER + SHIFT + comma', 'Dismiss all notifications', 'makoctl dismiss --all')
command('SUPER + CTRL + comma', 'Toggle notification silence', 'makoctl mode -t do-not-disturb')
command('SUPER + ALT + comma', 'Invoke notification', 'makoctl invoke')
command('SUPER + SHIFT + ALT + comma', 'Restore notification', 'makoctl restore')

-- Window, workspace, and group controls retain Omarchy's tiling-v2 keys.
bind('SUPER + W', 'Close window', d.window.close())
bind('SUPER + J', 'Toggle split', d.layout('togglesplit'))
bind('SUPER + P', 'Pseudo tile', d.window.pseudo())
bind('SUPER + T', 'Toggle floating', d.window.float({ action = 'toggle' }))
bind('SUPER + F', 'Fullscreen', d.window.fullscreen({ mode = 'fullscreen', action = 'toggle' }))
bind('SUPER + ALT + F', 'Full width', d.window.fullscreen({ mode = 'maximized', action = 'toggle' }))
bind('SUPER + CTRL + F', 'Tiled fullscreen', d.window.fullscreen_state({ internal = 0, client = 2, action = 'toggle' }))
bind('SUPER + O', 'Float and pin window', function()
  local window = hl.get_active_window()
  if not window then return end
  if window.pinned then
    hl.dispatch(d.window.pin({ action = 'unset' }))
    hl.dispatch(d.window.float({ action = 'unset' }))
  else
    hl.dispatch(d.window.float({ action = 'set' }))
    hl.dispatch(d.window.center())
    hl.dispatch(d.window.pin({ action = 'set' }))
  end
end)
bind('SUPER + L', 'Toggle dwindle/scrolling workspace', function()
  local workspace = hl.get_active_workspace()
  if workspace then
    hl.workspace_rule({ workspace = tostring(workspace.id), layout = workspace.tiled_layout == 'dwindle' and 'scrolling' or 'dwindle' })
  end
end)
for _, direction in ipairs({ 'left', 'right', 'up', 'down' }) do
  bind('SUPER + ' .. direction, 'Focus ' .. direction, d.focus({ direction = direction }))
  bind('SUPER + SHIFT + ' .. direction, 'Swap ' .. direction, d.window.swap({ direction = direction }))
  bind('SUPER + SHIFT + ALT + ' .. direction, 'Move workspace ' .. direction, d.workspace.move({ monitor = direction }))
  bind('SUPER + ALT + ' .. direction, 'Join group ' .. direction, d.window.move({ into_group = direction }))
end
for i = 1, 10 do
  local key = 'code:' .. (i + 9)
  bind('SUPER + ' .. key, 'Workspace ' .. i, d.focus({ workspace = i }))
  bind('SUPER + SHIFT + ' .. key, 'Move to workspace ' .. i, d.window.move({ workspace = i, follow = true }))
  bind('SUPER + SHIFT + ALT + ' .. key, 'Move silently to ' .. i, d.window.move({ workspace = i, follow = false }))
end
bind('SUPER + S', 'Scratchpad', d.workspace.toggle_special('scratchpad'))
bind('SUPER + ALT + S', 'Move to scratchpad', d.window.move({ workspace = 'special:scratchpad', follow = false }))
for key, workspace in pairs({ Tab = 'e+1', ['SHIFT + Tab'] = 'e-1', ['CTRL + Tab'] = 'previous', mouse_down = 'e+1', mouse_up = 'e-1' }) do
  bind('SUPER + ' .. key, 'Switch workspace', d.focus({ workspace = workspace }))
end
for key, next_window in pairs({ Tab = true, ['SHIFT + Tab'] = false }) do
  bind('ALT + ' .. key, 'Cycle windows', function()
    hl.dispatch(d.window.cycle_next({ next = next_window }))
    hl.dispatch(d.window.bring_to_top())
  end)
end
bind('CTRL + ALT + Tab', 'Next monitor', d.focus({ monitor = '+1' }))
bind('CTRL + ALT + SHIFT + Tab', 'Previous monitor', d.focus({ monitor = '-1' }))
for key, size in pairs({ ['code:20'] = {-100, 0}, ['code:21'] = {100, 0}, ['SHIFT + code:20'] = {0, -100}, ['SHIFT + code:21'] = {0, 100} }) do
  bind('SUPER + ' .. key, 'Resize window', d.window.resize({ x = size[1], y = size[2], relative = true }))
end
bind('SUPER + mouse:272', 'Move window', d.window.drag(), { mouse = true })
bind('SUPER + mouse:273', 'Resize window', d.window.resize(), { mouse = true })
bind('SUPER + G', 'Toggle group', d.group.toggle())
bind('SUPER + ALT + G', 'Leave group', d.window.move({ out_of_group = true }))
bind('SUPER + ALT + Tab', 'Next grouped window', d.group.next())
bind('SUPER + ALT + SHIFT + Tab', 'Previous grouped window', d.group.prev())
bind('SUPER + CTRL + left', 'Previous grouped window', d.group.prev())
bind('SUPER + CTRL + right', 'Next grouped window', d.group.next())
bind('SUPER + ALT + mouse_down', 'Next grouped window', d.group.next())
bind('SUPER + ALT + mouse_up', 'Previous grouped window', d.group.prev())
for i = 1, 5 do bind('SUPER + ALT + code:' .. (i + 9), 'Group window ' .. i, d.group.active({ index = i })) end
for key, shortcut in pairs({ C = { 'CTRL', 'Insert' }, V = { 'SHIFT', 'Insert' }, X = { 'CTRL', 'X' } }) do
  bind('SUPER + ' .. key, 'Universal clipboard', d.send_shortcut({ mods = shortcut[1], key = shortcut[2] }))
end

-- Media keys: same keys, direct PipeWire/brightness/playerctl commands, no OSD.
for key, action in pairs({ XF86AudioRaiseVolume = 'wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+', XF86AudioLowerVolume = 'wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-', XF86AudioMute = 'wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle', XF86AudioMicMute = 'wpctl set-mute @DEFAULT_AUDIO_SOURCE@ toggle', XF86MonBrightnessUp = 'brightnessctl set +5%', XF86MonBrightnessDown = 'brightnessctl set 5%-' }) do
  command(key, 'Media/brightness', action, { locked = true, repeating = true })
end
for key, action in pairs({ XF86AudioNext = 'next', XF86AudioPrev = 'previous', XF86AudioPlay = 'play-pause', XF86AudioPause = 'play-pause' }) do
  command(key, 'Media playback', 'playerctl ' .. action, { locked = true })
end
