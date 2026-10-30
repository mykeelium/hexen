# HEXEN screensaver

Hexen displays a large `HEX3N` wordmark with random TerminalTextEffects (TTE)
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

The artwork is `config/branding/screensaver.txt`. It contains a full-block-cell
raster of the HEX3N wordmark, so TTE can animate each filled terminal cell and
build the glyph shapes piece by piece. Invisible Braille blank characters keep
empty cells aligned. The raster is sampled from the actual custom H, E, 3, and
N outlines; X is composed from the JetBrainsMono Nerd Font fallback.
`config/ghostty/screensaver.ghostty` controls the smaller terminal
font needed to fit the 64-column art and its black backdrop, independently of
the normal terminal theme and shaders.

After editing the SVG paths, rebuild the custom font and then regenerate the
full-block artwork:

```sh
python tools/build_hexen_glyph_font.py
python tools/render_hexen_screensaver.py
```

FontTools (`python-fonttools` on Arch) and Pillow (`python-pillow`) are needed
for regeneration only. The generated artwork is checked in, so the installed
screensaver has no Pillow dependency. All four custom glyphs share a common
outline box and side bearing, and N/3 are generated as exact horizontal
reflections of H/E. The same font shapes the lock-screen wordmark. Path
outlines become filled glyphs in the current text color; SVG fill and stroke
styling is not embedded as font color. Ansible installs the generated font for
the desktop user and refreshes that user's font cache. The screensaver runs at
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
