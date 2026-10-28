# Desktop setup and editable Omarchy-style bindings

The first desktop targets the VM's Hyprland 0.56.2 with Lua configuration.
Omarchy's local revision `8e03151647ef210ce9e313180e642d3e58dbe9a6` supplied the
binding reference, especially `default/hypr/bindings/tiling-v2.conf` and app
bindings. Its license is retained in [licenses/omarchy.txt](licenses/omarchy.txt).
No host desktop configuration or Omarchy source was changed.

The owner asked to stay close to Omarchy defaults and keep shortcuts easy to
change. The file to edit is [`config/hypr/bindings.lua`](../config/hypr/bindings.lua).
The role links it through the selected user's config directory, so saving the
repository file changes the desktop configuration. After editing, run
`hyprctl reload` and `hyprctl configerrors`. A private per-machine
`config/hypr/local.lua` can override settings or unbind/rebind shortcuts last;
this file is git-ignored. Keep shared changes in the tracked files.

## Provision and start

For a fresh setup, clone this repository into the target user's writable home
directory and run [`install/provision.sh`](../install/provision.sh) from any
terminal. It shows an interactive summary, installs the declared Ansible
collection, and runs the full workstation playbook for the logged-in account.
Keep the clone at the same path because the configuration links point into it.
For manual control, the equivalent commands from the repository root are:

```sh
export ANSIBLE_CONFIG="$PWD/ansible/ansible.cfg"
ansible-playbook -i ansible/inventory/localhost.yml ansible/playbook.yml \
  -e desktop_user=YOUR_USER --ask-become-pass
```

`desktop_user` must name an existing non-root account. Omitting it runs only
boot/base/apps, preserving the earlier provisioning path. The desktop role
checks targets before changing packages: existing config directories, foreign
symlinks, and redirected parents are refused. Existing real user-owned parent
permissions are preserved. Move/back up and reconcile unmanaged configs yourself;
the provisioner does not overwrite them.

Log into the VM as that user on an active local TTY and run:

```sh
uwsm start hyprland.desktop
```

There is no persistent autologin or display-manager configuration. The desktop
role installs the official Arch `sd` package and the checksum-pinned LocalSend
AppImage for the desktop user. Run the [editor setup](../config/nvim/README.md)
as the same user. Do not run Hyprland or Neovim setup as root. The agent's temporary `hexen-desktop-test2` service only
provides a test login in the disposable VM; it disappears on reboot.

## Binding coverage and deliberate differences

| Keys | Action |
| --- | --- |
| Super+Enter / Super+Alt+Enter | Ghostty / Zellij (`Work` session) |
| Super+Shift+Enter or B | Zen Browser; reports missing package until manually installed |
| Super+Shift+Alt+B | Private Zen window |
| Super+Shift+N / O / F | Owner Neovim / Obsidian / Nautilus |
| Super+Shift+I | Bluetui in a centered floating Ghostty window |
| Super+Shift+/ | 1Password; requires manual installation |
| Super+Space | Selected application launcher through `hexen-desktop` |
| Super+Alt+Space / Super+Escape | Hexen menu / system menu |
| Super+K | View/edit the binding file in Neovim |
| Super+W / J / P / T | Close / split / pseudo / floating |
| Super+F / Alt+F / Ctrl+F | Fullscreen / maximized / client fullscreen |
| Super+O / L | Float-and-pin / dwindle-scrolling workspace toggle |
| Super+arrows / Shift+arrows | Focus / swap windows |
| Super+1–0 / Shift+1–0 / Shift+Alt+1–0 | Select / move / silently move workspace |
| Super+Tab / Shift+Tab / Ctrl+Tab | Next / previous / former workspace |
| Super+S / Alt+S | Scratchpad / move to scratchpad |
| Super+G and group modifier variants | Group windows and navigate groups |
| Super+minus/equal and Shift variants | Resize |
| Super+mouse buttons / scroll | Move/resize windows / cycle workspaces |
| Super+C / V / X | Universal copy/paste/cut |
| Super+Ctrl+V / Print | Clipboard history / region screenshot to clipboard |
| Super+Ctrl+L | Lock through loginctl/hypridle/hyprlock |
| Super+comma and modifier variants | Notification controls |
| Media and brightness keys | PipeWire volume, playerctl playback, brightnessctl |

There are 121 registered shortcuts in the tested VM. Core window/workspace/group
keys follow Omarchy. Helper-backed actions use small repository-owned commands
rather than installing Omarchy's framework:

- Fuzzel is the default launcher from official Arch repositories. Walker is an
  install-time option using manually built, pinned Walker/Elephant recipes and
  selected providers; see [the build procedure](../install/manual-apps/walker/).
  Provisioning asks for the choice and checks that Walker's packages already
  exist. It never builds AUR recipes. `hexen-desktop` routes Super+Space,
  Super+Escape, the Hexen menu, Waybar pickers, and clipboard selection through
  that choice. Walker starts Elephant as a user service and exposes app search,
  files, command running, calculations, and provider navigation. Package search,
  AUR, Bluetooth, and clipboard providers are not enabled; cliphist remains the
  clipboard history implementation. Re-running provisioning changes the
  selected backend; an old backend config link may remain but is unused. An
  already-running Walker/Elephant process can remain in the current session
  until logout; the next login starts the selected session integration.
  Menus and Super+K expose this project's config.
- Ghostty replaces Omarchy's terminal resolver. Working-directory inheritance and
  launch-or-focus behavior are not implemented yet.
- Zellij attaches to or creates a named `Work` session. `zoxide` provides the
  `z` Bash command; rupa's `z` package is also installed under the `j` alias to
  avoid a command-name collision. Both tools maintain directory history locally.
- Window pop keeps float/pin semantics but does not apply Omarchy's fixed size.
- Screenshots copy a selected region to the clipboard; annotation, recording,
  OCR, color picking, and share/transcode/reminder menus are not implemented.
- The media keys call native tools without SwayOSD. Touchpad, keyboard-backlight,
  monitor-scaling/mirroring, night-light, and dictation helpers are not included.
- Optional Omarchy application/web-app keys are omitted when those apps/accounts
  are not selected. No Spotify, Signal, Docker, HEY, or web-account assumptions.
- System-menu actions are explicit selections. The menu does not run an arbitrary
  typed shell command. It does not silently power off on opening.

Waybar follows Omarchy's compact layout: the Hexen menu button and persistent
workspaces sit at the left, the clock is centered, and CPU, network, audio,
battery, and tray indicators sit at the right. Clicking the menu mark opens the
repo-owned menu; clicking the battery opens the same system picker as
Super+Escape. The picker offers lock, suspend, logout, restart, and shutdown.
Audio click toggles mute and scroll adjusts volume. The bar omits
Omarchy indicators that depend on its own updater, recording, idle-toggle,
notification, and voice-typing services.

Unavailable actions are omitted rather than bound to absent `omarchy-*` scripts.
Further bindings can be added to the same file without adopting the framework.

## Packages, services, and data

The reviewed common package list is in `ansible/roles/desktop/defaults/main.yml`.
These packages come from Arch's signed official repositories; the selected
launcher defaults to the separately reviewed manual Walker package set, with
official Fuzzel available as an alternative. Common packages include the
compositor, Ghostty, Zellij, Waybar, Mako, Nautilus, lock/idle tools, PipeWire/WirePlumber,
Hyprland/GTK portals, BlueZ/Bluetui Bluetooth support, audio device controls,
Polkit agent, clipboard/capture tools, fonts, and the
build and language runtimes used by the owner editor. It also installs the virt-manager
QEMU/KVM host stack, with system libvirt sockets and the default NAT network.
See [virtualization setup](virtualization.md) for guest isolation and authorization.
The default VM storage pool is `/var/lib/libvirt/images`; an existing custom
pool is preserved and must be selected explicitly if it replaces that path.
Dependencies are substantial;
the installed manifest and package diff are recorded in the VM checkpoint folder.
No additional pacman repository or AUR helper is added. Walker builds and
updates stay manual; the setup only checks for the packages when Walker is
selected.

OBS Studio is installed from Arch's signed official `extra/obs-studio` package
through the apps role; the package source review records that it was flagged
out-of-date on 2026-10-23. This does not use AUR. The desktop role enables
`bluetooth.service`; press Super+Shift+I to launch Bluetui and pair/connect
headphones, then use
`pavucontrol` or the Zoom audio settings to choose the headset output and
microphone. PipeWire/WirePlumber supplies Bluetooth audio. If the headset
microphone is selected, Bluetooth may switch to its call profile, which can
reduce playback quality; using the computer or an external microphone keeps the
headphones in a higher quality playback profile.

## Meetings and recording

The Wayland screen-capture path is already configured: Hyprland's XDG portal
backend is selected for ScreenCast, and PipeWire is started with the user
session. Zoom can use that portal to share the **entire desktop**. Zoom's Linux
client does not support selecting one application window in a Wayland session;
its documented options are whole-desktop sharing or a whiteboard. Use an Xorg
session if single-window sharing is a hard requirement. Before a meeting, check
Zoom's selected microphone, speaker, and camera. For screen sharing, choose the
entire display in Zoom and confirm the portal prompt.

For OBS on Hyprland, add a **Screen Capture (PipeWire)** source and approve the
portal prompt. Add audio output and microphone capture sources if the recording
needs sound. The current repository setup prepares the packages and portal path;
it does not pre-create an OBS scene or choose a monitor-specific recording
profile.

Before relying on this on the laptop, complete a real acceptance pass: connect
the Bluetooth headset, test Zoom microphone/speaker/camera, share the whole
desktop and confirm it is visible to a participant, then record an OBS clip with
the intended audio sources and play it back. The VM's virtual devices cannot
prove the laptop's Bluetooth adapter, camera, microphone, or audio profiles.

These tools and the requested CLI utilities are installed from Arch's signed
official `extra` repository; see the [package source inventory](app-sources.md#requested-cli-utilities).
The selected Tokyo Night pack supplies Ghostty's initial palette. The Bash setup also
sets `cat` to `bat --paging=never` for interactive use.
The desktop role adds a marked block to the target user's `.bashrc`; it does not
replace the rest of that file.
It also adds a marked block to `.gitconfig` to use delta for Git diffs. This
preserves existing Git settings outside the managed block. Podman and
`podman-compose` provide rootless containers through the selected desktop
user. The user socket is enabled for interactive logins; linger is not enabled.
LazyDocker uses that Docker-compatible Podman socket through a Bash function,
and its Compose commands use `podman compose`. The literal `docker` executable
is not shimmed, leaving Docker Engine available to add later for individual
compatibility cases. The socket stays on the local user runtime path; no TCP API
listener is enabled.

The desktop role installs Mono from Arch's signed `extra` repository. Mono is a
native Linux implementation of much of the .NET Framework
4.7 API surface and includes 4.7.2 reference assemblies; run compatible managed
executables with `mono /path/to/app.exe`. Rider can use Mono/XBuild for legacy
.NET Framework projects, while `dotnet-sdk` remains the modern .NET SDK. Mono
is not Microsoft's .NET Framework runtime and does not implement every Windows
API. In particular, WPF is not implemented, and WCF/ASP.NET support is limited.
Check the app's dependencies before relying on it. See [the source notes](app-sources.md#running-windows-net-framework-applications).

Hyprland starts the bar, notification daemon, Polkit agent, idle daemon, and
clipboard watchers. It imports the Wayland environment for user services and
starts PipeWire sockets/WirePlumber. Portal selection uses the Hyprland backend
for screen capture and GTK for file choosing. The installed keyring still needs
interactive unlock/integration testing before work-account sign-in.

Clipboard history is stored under the user's local cache by cliphist. Remove
the two `wl-paste --watch` startup lines to disable storage; `cliphist wipe`
clears history. The idle policy locks at five minutes and blanks displays at ten;
it does not suspend or hibernate. Manual lock uses the same lock daemon.

## Named desktop themes

The desktop role installs Matugen and Hyprpaper from Arch's signed `extra`
repository. It initializes the `tokyo-night` pack on first provisioning.
Run `hexen-theme create` for the guided wallpaper builder. It asks for a name,
image path, dark/light mode, Matugen scheme, and wallpaper fit. It copies the
wallpaper into a new pack under `config/themes/`, validates the image with
Matugen, and offers to apply the new theme. This keeps the wallpaper with the
repo so the pack is reproducible. Review and commit the new pack if you want it
included in future installs. The **Create Theme** launcher opens this command
in Ghostty. For manual curation, copy an existing theme pack and edit its
`theme.toml` or `palette.json`.

`hexen-theme list`, `hexen-theme current`, and `hexen-theme apply <slug>` are
also available from a terminal. The Hexen menu includes **Themes**, and the
desktop application list includes both **Themes** and **Create Theme**.

Theme manifests support `name`, `mode` (`dark` or `light`), Matugen `type`, an
optional `palette` JSON file, an optional `wallpaper`, and wallpaper `fit_mode`
(`cover`, `contain`, `fill`, or `tile`). For a wallpaper, Matugen uses the
manifest's mode and scheme to derive colors; otherwise it renders the curated
palette exactly. Relative wallpaper
paths must stay inside the theme pack. Absolute paths can reference a local
image outside the repository. Theme packs never download or execute third-party
hooks.

Generated app fragments and the active theme link live in
`${XDG_STATE_HOME:-~/.local/state}/hexen/themes`, outside the repository. The
Ansible role defaults `desktop_xdg_state_home` to `~/.local/state`; override it
when provisioning if you use a different state directory. The role persists
the configured path in `~/.config/hexen/state-home`, which the theme helper
uses ahead of `XDG_STATE_HOME` so graphical launches share the same state. The
role also exports it in its managed Bash setup and passes it to initial theme
selection. App configs load the active generation through the stable
`~/.config/hexen/theme` link. The shared app layouts remain in this repository,
while generated colors are included by Hyprland, Waybar, Ghostty, Mako,
Fuzzel/Walker, Hyprlock, and Hyprpaper. Hyprpaper starts with Hyprland and restores the selected pack's
wallpaper after login. Applying a theme reloads Hyprland, Waybar, and Mako,
restarts Walker's `--gapplication-service` so it loads the new CSS and app
catalog, and restarts Hyprpaper from the selected generated config. It asks
Ghostty's systemd user service to reload and sends Ghostty's documented reload
signal directly when that service is inactive. If rendering or live wallpaper
activation fails, the previously active theme stays selected. Neovim keeps its
independent colorscheme. See
[`config/themes/README.md`](../config/themes/README.md) for pack creation and
manifest details.

## Verification and remaining acceptance

The existing temporary VM acceptance below predates the switch from Foot to
Ghostty. The desktop role now validates Ghostty's configuration during
provisioning; the VM needs a reprovision and a new login before the terminal
change is confirmed there. Its previous session rendered the bar and Foot,
ran Mako and the portal/audio services, and had no failed user
units. Actual injected Super+2, Super+Enter, and Super+Space keys switched
workspace, opened a terminal, and opened the launcher. Synthetic clipboard
round-trip passed. Both native keyboard and pointer devices are enumerated.
Idle locking rendered successfully. After the owner unlocked the desktop,
Super+Shift+N opened the merged editor visibly, Super+F toggled fullscreen, and
Super+Shift+O opened Obsidian's initial vault-selection window. No account was
signed in and no vault was created.

`tests/editor-project.lua` created a temporary dependency-free Go module. gopls
attached and returned variable-hover information; Delve launched the program and
stopped on entry through nvim-dap-go. The test removed the project and terminated
the debugger; no Delve process remained. Other language/project workflows,
meeting screen sharing, and manual third-party applications remain pending.

The initial test harness launched Hyprland before activating its VT, so its first
session missed input devices. Restarting on an already active VT fixed it;
normal users should start from their active local login. No input-group membership
or device-permission relaxation was used. Optional VM Bluetooth/RealtimeKit
messages are present; actual laptop devices and audio/video still need testing.

Regression commands inside the disposable VM (root):

```sh
ANSIBLE_ROLES_PATH=ansible/roles ansible-playbook -i localhost, \
  tests/desktop.yml -e test_desktop_user=YOUR_USER
ANSIBLE_ROLES_PATH=ansible/roles ansible-playbook -i localhost, \
  tests/desktop-metadata.yml -e test_desktop_user=YOUR_USER
```

The metadata test temporarily makes `.config` private and restores its original
mode; it also creates and removes an isolated locked test account. Use the
`test_desktop_user` argument, not `desktop_user`, so refusal cases can override
the fixture account without Ansible extra-variable precedence masking them.

The [HEXEN screensaver guide](screensaver.md) covers idle animation, manual
preview, artwork customization, and its separate authentication policy.

## Display settings and Walker searches

Open **Super+Alt+Space → Display settings** for Hyprmon's monitor arrangement
screen. [Install its pinned Lua-capable build](../install/manual-apps/hyprmon/)
first. Saved layouts are machine state and do not rewrite the shared config.

When Walker is selected, open it with **Super+Space**:

| Type | Result |
| --- | --- |
| `2+2` | Calculator result alongside application matching |
| `=2+2` | Calculator only |
| `a phrase with no matching app` | Google search fallback |
| `@your search phrase` | Explicit web search, even when an app matches |

The calculator is Elephant's `calc` provider. The added `websearch` provider
uses Google and is hidden when app/calculator results exist. Opening the search
requires selecting it and pressing Enter. Typing a phrase alone does not open
a browser or submit the phrase to Google. Web-search history is disabled.
Selecting the Google result sends its URL to `xdg-open`, so an HTTP/HTTPS
browser handler must be available. Zen is the chosen browser: in the clean VM,
installing Zen registered `zen.desktop` as the handler, and `xdg-open` started
Zen with a Google test URL. Check
`xdg-mime query default x-scheme-handler/https` on machines that already have
another browser.

Install the matching `elephant-websearch` package using the updated
[Walker build instructions](../install/manual-apps/walker/) before selecting
Walker in provisioning. Providers must match the pinned Elephant build; adding
an arbitrary newer plugin can cause a Go plugin version mismatch. These Walker
provider settings do not change the Fuzzel launcher.

## Terminal prompt

The install includes Arch's `starship` package and links `config/starship.toml`
to `~/.config/starship.toml`. The prompt matches the current cyan configuration:
current directory, Git branch/status, and ❯ after success or ✗ after failure.
The desktop role adds a marked Starship initialization block to `.bashrc`,
preserving other shell configuration. Open a new Bash terminal after provisioning.
Repeated sourcing does not register Starship twice; nested interactive shells
initialize their own prompt. Non-interactive Bash sessions do not initialize it.

An existing unmanaged Starship configuration is preserved: desktop preflight
refuses to replace it. Move it aside yourself after reviewing it if you want to
adopt the repository version. Font glyphs use the already installed Nerd Font.

## Lock screen

Press **Super+Ctrl+L** (or choose Lock in the system menu) to lock the session.
Hyprlock shows the HEXEN wordmark, clock, account name and an explicit locked
status. The password field remains visible before typing. Enter your password
and press Enter to unlock; an unsuccessful attempt displays an unlock-failure
message. Colors follow the active Hexen theme. This is a visual update only:
PAM authentication and the idle/suspend locking policy remain unchanged.
