# Hyprmon for Hexen

The tested upstream source is commit `32ad27f94f40fd0dd81f982cc8208bb615607202`
from https://github.com/erans/hyprmon. This is newer than v0.0.16 and includes
Lua-aware live application and saving, needed by Hexen's Hyprland 0.56 setup.
Upstream tests passed for this commit. The module requires Go 1.26; Go may fetch
that toolchain automatically if your installed version is older.

Build as your normal user, after reviewing the source and Go module files:

```sh
mkdir -p "$HOME/build"
git clone https://github.com/erans/hyprmon.git "$HOME/build/hexen-hyprmon"
cd "$HOME/build/hexen-hyprmon"
git checkout 32ad27f94f40fd0dd81f982cc8208bb615607202
go test ./...
go build -trimpath -o hyprmon .
install -b -Dm755 hyprmon "$HOME/.local/bin/hyprmon"
```

The installation backs up an existing binary. Provisioning does not build or
update this manually installed application. Review a new upstream commit and
repeat the build when upgrading it.

Open **Super+Alt+Space → Display settings**. This opens Hyprmon in Ghostty using
`hexen-desktop monitors`. Use this entrypoint instead of running bare `hyprmon`,
so saved monitor settings stay outside the linked repository configuration.

- Arrow keys move the selected display; Tab selects another display.
- R selects scale; F selects resolution/refresh rate.
- A applies the arrangement live; S saves it; Z reverts; Q exits.

The launcher passes a machine-local `HYPRLAND_CONFIG` target under
`$XDG_STATE_HOME/hexen/displays/` (default `~/.local/state/hexen/displays/`). It
honors the `~/.config/hexen/state-home` marker written by provisioning. Hyprmon
writes its generated `hyprmon.lua` there, which Hexen loads after its generic
monitor rule. Existing `~/.config/hypr/local.lua` overrides still load last.
This preserves the repository's default configuration across machines.

Profiles and Hyprmon preferences remain under `~/.config/hyprmon/`. A applies an arrangement immediately without saving it. S saves the layout
and immediately reloads Hyprland, applying the saved arrangement too. Physical docking/lid/monitor acceptance stays with the deferred
hardware phase; this patch does not enable automatic profile switching.
