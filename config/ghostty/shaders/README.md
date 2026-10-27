# Ghostty cursor shaders

These shaders are vendored from [sahaj-b/cursor-shaders](https://github.com/sahaj-b/cursor-shaders), retrieved from its `main` branch on 2026-10-27:

- `cursor_warp.glsl`: [upstream source](https://github.com/sahaj-b/cursor-shaders/blob/main/ghostty/cursor_warp.glsl)
- `ripple_cursor.glsl`: [upstream source](https://github.com/sahaj-b/cursor-shaders/blob/main/ghostty/ripple_cursor.glsl)
- `LICENSE`: upstream MIT license

The source is checked into this repository. Setup does not clone, download, or execute upstream code at install or runtime. The only source modifications are the requested configuration constants at the top of each shader.

SHA-256 checksums for this vendored snapshot:

| File | SHA-256 |
| --- | --- |
| `cursor_warp.glsl` | `d43432ca7939a2be4f8d74702401943c25a4544338379652345b20bb66f7f9a8` |
| `ripple_cursor.glsl` | `5c6c00e1f7933cddb881f909a262d8923d0c84d7c4915f98c7ebc1c309c608a6` |
| `LICENSE` | `d302680270506293d42ef8874d70e2603c4e3f1b39bbdd800447de70449aff7d` |

Ghostty loads `cursor_warp.glsl` followed by `ripple_cursor.glsl`; order matters. `custom-shader-animation = always` keeps the short ripple animating when a Ghostty surface loses focus. It may use more GPU time while unfocused.

To disable the effect, comment out the two `custom-shader` lines and the animation setting in `config.ghostty`. If a shader error makes a terminal window unusable, edit that config from another terminal or a TTY and restart Ghostty. Rendering should be checked on the target machine/GPU.
