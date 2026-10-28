# HEXEN screensaver

Hexen displays a large `HEXEN` wordmark with random TerminalTextEffects (TTE)
animations in fullscreen Ghostty windows, one on each active, non-mirrored
monitor. The backdrop is black, with the text cursor hidden inside the terminal.

After provisioning, log out and back into Hyprland to load the idle settings.
Leave the desktop idle for 2½ minutes to start the animation. Press a key, click, scroll, or move
the mouse to dismiss it. The five-minute session lock remains enabled; the
screensaver also requests that lock after another 2½ minutes when launched by
Hypridle, because opening terminal windows can reset compositor idle timers.
Once locked, displays turn off after five further idle minutes (about ten
minutes from the initial activity). A ten-minute fallback listener also remains.
A manually locked session similarly powers off after five idle minutes.

The animation is decorative: Hyprlock still authenticates you. It does not run
when Hyprlock is already active and closes when Hyprlock starts. It never kills
unrelated terminals or TTE processes. If an automatic animation fails after
opening its windows, the helper locks early to keep that failure from extending
the security deadline.

To preview it immediately:

1. Open the Hexen menu with **Super+Alt+Space**.
2. Choose **Screensaver**.
3. Press a key or move the mouse to return to your desktop.

You can also run these commands in a graphical-session terminal:

```sh
hexen-desktop screensaver
# From another terminal, if needed:
hexen-screensaver stop
```

Manual previews use the existing idle policy; they do not start the extra
2½-minute lock deadline used for automatic idle launches.

The artwork is `config/branding/screensaver.txt`. Edit it to change the wordmark.
`config/ghostty/screensaver.ghostty` controls its font size and black backdrop,
independently of the normal terminal theme and shaders. The animation runs at
60 frames per second. TTE selects a random effect each time one completes.

TTE 0.15.0 is downloaded from its official PyPI release as a checksum-pinned wheel
to `~/.local/share/hexen/screensaver/`. Existing `uv` runs it in an isolated cached
environment with network access disabled. Provisioning downloads the wheel and
prepares that cache; normal use needs no network and installs nothing into
system Python. The helper and wheel are managed by the desktop Ansible role.

The private controller socket and lock live under `$XDG_RUNTIME_DIR`, scoped to
the Hyprland instance. Repeated starts share one controller. Stopping terminates
only process groups created by that controller; terminal exit or animation
failure closes the remaining screensaver windows.

To disable automatic animation, remove the 150-second listener from
`config/hypr/hypridle.conf`, then log out and back in. Keep the lock and
screen-power listeners below it. The menu preview remains available.

Run controller and PTY regression tests with:

```sh
python -m unittest discover -s tests -p 'test_*.py'
```

Upstream: [TerminalTextEffects](https://github.com/ChrisBuilds/terminaltexteffects).
