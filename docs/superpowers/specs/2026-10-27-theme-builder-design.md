# Theme Builder Design

## Intent

Make creating a reproducible desktop theme straightforward for the owner without
requiring manual JSON or TOML editing. The builder belongs in this repository:
the existing theme packs and renderer already live here, and the target system
uses a writable clone of the repository.

## Approaches

- **Guided terminal builder (selected):** extend `hexen-theme` with an
  interactive `create` command, and expose it as a launcher application. This
  reuses Python's standard library and the existing Matugen renderer.
- **Graphical editor:** provide image preview and manual color controls. This
  adds UI code and dependencies and is not needed to create wallpaper-derived
  themes.

## Behavior

The builder asks for a display name, a local wallpaper image, dark or light
mode, a Matugen color scheme, and wallpaper fit mode. It derives a lowercase
hyphenated directory name, copies the image into that theme pack, and writes a
`theme.toml` that points to the copied image. The image stays with the pack so
the theme is reproducible from the repository. Matugen extracts the palette
directly from this image; the user does not need to create or edit a palette
file. The existing renderer uses the selected mode and scheme to generate the
app colors, and the shared templates map those colors to each app. The builder
refuses to overwrite an existing pack and removes any partial pack if creation
is cancelled or fails.

After creating a valid pack, it offers to apply it through the existing theme
renderer. Applying continues to generate app configuration into user state,
outside the repository. Existing curated palette packs are unaffected.

The command is `hexen-theme create`. A desktop application entry launches it in
Ghostty so it is available through Walker or other desktop application menus.
The existing desktop role links the script and application entry from the repo;
no additional runtime package is required beyond the existing Python and
Matugen dependencies.

## Boundaries

The first version supports local image files and Matugen's currently accepted
schemes. It does not provide a visual image preview or manual per-app color
editor. Those remain possible later extensions to the same theme pack format.
