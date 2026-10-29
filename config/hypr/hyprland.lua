-- Hexen: repository-owned configuration for Hyprland 0.56+.
local directory = os.getenv('HOME') .. '/.config/hypr/'
package.path = directory .. '?.lua;' .. package.path
require('theme')
local generated_theme = os.getenv('HOME') .. '/.config/hexen/theme/hyprland.lua'
local generated_theme_file = io.open(generated_theme, 'r')
if generated_theme_file then generated_theme_file:close(); dofile(generated_theme) end
require('bindings')
hl.monitor({ output = '', mode = 'preferred', position = 'auto', scale = 'auto' })
require('monitors')
hl.config({
  input = { kb_layout = 'us', follow_mouse = 1, touchpad = { natural_scroll = true } },
  general = { layout = 'dwindle' },
  dwindle = { preserve_split = true },
  misc = { disable_hyprland_logo = true, force_default_wallpaper = 0 },
})
hl.window_rule({
  match = { class = "^io[.]github[.]hexen[.]bluetui$" },
  float = true,
  center = true,
  size = { "monitor_w*0.45", "monitor_h*0.5" },
})
hl.window_rule({
  match = { class = "^io[.]github[.]hexen[.]updatereview$" },
  float = true,
  center = true,
  size = { "monitor_w*0.68", "monitor_h*0.76" },
})
hl.env('XDG_CURRENT_DESKTOP', 'Hyprland')
hl.env('XDG_SESSION_TYPE', 'wayland')
hl.on('hyprland.start', function()
  hl.exec_cmd('dbus-update-activation-environment --systemd WAYLAND_DISPLAY HYPRLAND_INSTANCE_SIGNATURE XDG_CURRENT_DESKTOP XDG_SESSION_TYPE && systemctl --user start pipewire.socket pipewire-pulse.socket wireplumber.service && "$HOME/.local/bin/hexen-desktop" start-session')
  hl.exec_cmd('/usr/lib/polkit-gnome/polkit-gnome-authentication-agent-1')
  hl.exec_cmd('waybar')
  hl.exec_cmd('mako')
  hl.exec_cmd('hyprpaper')
  hl.exec_cmd('hypridle')
  -- Clipboard history is local to this user. Remove these to disable storage.
  hl.exec_cmd('wl-paste --type text --watch cliphist store')
  hl.exec_cmd('wl-paste --type image --watch cliphist store')
end)
-- Put machine-specific monitors/settings here; this file is never provisioned.
local local_file = directory .. 'local.lua'
local file = io.open(local_file, 'r')
if file then file:close(); dofile(local_file) end
