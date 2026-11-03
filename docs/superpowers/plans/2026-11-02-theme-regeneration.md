# Selected theme regeneration

**Goal:** regenerate the selected theme during provisioning after repository or
renderer updates, preserving selection and zero-change reruns.

**Design:** render and compare the generated app fragments before activation.
This deliberately trades rendering time for avoiding an incomplete input/cache
fingerprint. Matugen upgrades and external wallpaper changes are covered by the
same comparison; a saved wallpaper SHA-256 detects changed images even when
their extracted colors remain identical. Generated Matugen configuration contains temporary paths and
is excluded from comparison. Existing theme-pack formats remain unchanged.

**Spec:** [named theme packs](../specs/2026-10-27-theme-packs-design.md).

## Constraints

- Work on the current branch; preserve unrelated pending edits.
- Preserve the selected slug. Only an installation with no selection defaults
  to Tokyo Night; an invalid selection fails instead of silently resetting.
- Render failure leaves the active generated theme unchanged.
- Compare generated Hyprland, Waybar, Ghostty, Mako, Fuzzel, Walker, Hyprlock,
  Hyprpaper, wallpaper digest and slug files; temporary renderer configuration
  is not an app input. Legacy output without a digest is regenerated once.
- Check mode may use temporary staging but must not create persistent theme
  state, switch links or reload desktop processes.
- First-install Ansible check mode reports pending regeneration when Matugen is
  not installed yet, without claiming a rendered preview.
- Reuse existing desktop refresh behavior only after changed output activates.
  Headless provisioning does not discover or attach to graphical sessions.

## Implementation

- [x] Add CLI regression tests using a temporary home, checkout and fake Matugen
  process. Cover initial state, unchanged reruns, selected-pack preservation,
  changed templates/palette/wallpaper, missing output, render failure and preview.
- [x] Add `hexen-theme sync [--check]`, with JSON `changed` and `slug` fields,
  reusing the existing staged rendering and atomic activation path.
- [x] Replace first-install-only initialization with an Ansible sync task that
  runs a preview during check mode and reports changes from the JSON result.
- [x] Exercise that Ansible task against an isolated fixture without system
  package/service changes; document behavior and remaining VM acceptance.
- [x] Run focused and full regression checks, syntax validation and code review.

## Verification results

- All 77 Python tests passed, including 15 theme synchronization tests and the
  real Ansible task running against an isolated home/checkout with fake Matugen.
- The full Ansible playbook passed syntax validation with Ansible Core 2.19.15
  and the repository-pinned `community.general` 13.5.0 collection in `/tmp`.
- Review identified first-install check mode with no Matugen installed. Its
  integration case failed before the fix and passed afterward; Ansible now
  reports an unavailable rendered preview and pending regeneration.
- A wallpaper change with identical extracted colors also failed before the
  digest comparison was added and passed afterward.
- Preview/no-op tests confirm no desktop reload; a changed live-session fixture
  exercises existing refresh dispatch without controlling the host desktop.

No real Matugen render, graphical reload, or installed-VM provisioning was
performed by these fixtures. Those checks remain in candidate acceptance.

Changes remain uncommitted for owner review. Full desktop reload and installed
VM acceptance remain distinct from fixture-based regression tests.
