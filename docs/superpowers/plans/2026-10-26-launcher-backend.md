# Install-Time Launcher Backend Implementation Plan

> **For agentic workers:** Implement each task inline in the current workspace. The plan's validation steps are static inspection only; do not add or run tests.

**Goal:** Let provisioning select Fuzzel or Walker and consistently configure packages, menus, keybindings, themes, and session startup for that choice.

**Architecture:** Keep Fuzzel as the default official package. Walker packages are manually built from the reviewed AUR recipe commits and verified upstream release archives before provisioning; Ansible only checks and configures those packages. One `hexen-desktop` dispatcher reads the installed selection and serves the app launcher and dmenu menus.

**Tech Stack:** Bash, Ansible, Hyprland Lua, Fuzzel, Walker, Elephant, Arch `makepkg`/pacman.

**Spec:** `docs/superpowers/specs/2026-10-26-launcher-backend-design.md`

## Global Constraints

- Default `desktop_launcher` to `fuzzel`; accept only `fuzzel` or `walker`.
- Do not add AUR helpers, third-party pacman repositories, or automatic AUR builds to provisioning.
- Walker packages are manually built as a normal user from the recipe commits and source hashes in the spec.
- Keep clipboard history on cliphist; do not install Walker's clipboard provider or Arch package-management provider.
- Keep existing Super+Space, Super+Escape, Super+Alt+Space, and Waybar menu entry points available.
- Do not add or run tests. Use read-only code review and syntax/config checks only if needed.

## Review Focus

- Invalid backend values must fail before Ansible changes the machine.
- Walker selection without its manually installed packages/providers must fail with an actionable message before role changes.
- Fuzzel selection must not require Walker, Elephant, or their AUR packages.
- Cancelling any Fuzzel/Walker dmenu must not execute a system action or corrupt a pipeline.
- Helper calls from Waybar, Hyprland, and standalone shell sessions must resolve the same configured backend or safely default to Fuzzel.

---

### Task 1: Document and pin Walker package builds

**Files:**
- Create: `install/manual-apps/walker/README.md`
- Create: `install/manual-apps/walker/sources.lock`
- Modify: `install/manual-apps/README.md`
- Modify: `docs/app-sources.md`
- Modify: `docs/desktop.md`

**Interfaces:**
- Consumes: recipe commits, upstream versions, and SHA-256 values in the design spec.
- Produces: a manual build/install procedure for Walker, Elephant, and the five selected providers: desktopapplications, files, runner, calc, providerlist.

- [ ] Record that the AUR recipe commits are community-maintained; source archives come from upstream GitHub release tags and are SHA-256 checked.
- [ ] Give exact clone/checkout, inspection, `makepkg --verifysource`, unprivileged build, archive inspection, and explicit `pacman -U` steps. No helper or automated package build.
- [ ] Explain that Walker packages must be installed before selecting Walker in provisioning, and that updates require another recipe/source review.
- [ ] Update the desktop package/source docs to distinguish official packages from the manually selected Walker package set.
- [ ] Read the resulting docs and source lock to ensure every package and pin from the spec is present and no unreviewed provider was added.

### Task 2: Add install-time selection and package/config preflight

**Files:**
- Modify: `install/provision.sh`
- Modify: `ansible/roles/desktop/defaults/main.yml`
- Modify: `ansible/roles/desktop/tasks/preflight.yml`
- Modify: `ansible/roles/desktop/tasks/main.yml`

**Interfaces:**
- Consumes: install-time `desktop_launcher` choice (`fuzzel` or `walker`).
- Produces: conditional official package selection, config links, and early validation of Walker binaries/providers.

- [ ] Ask for the launcher after the existing provisioning confirmation, defaulting Enter to `fuzzel`, and pass `desktop_launcher` to both Ansible invocations.
- [ ] Validate the selection in Ansible defaults/preflight and before running Ansible in the shell entrypoint.
- [ ] Split common desktop packages from launcher-specific packages; install official `fuzzel` only for the Fuzzel selection.
- [ ] For Walker, check `walker`, `elephant`, and the five provider files under `/usr/lib/elephant/` before package/config mutation; print the manual build guide when any are missing.
- [ ] Link only the selected launcher's config directory, retaining current unmanaged-config refusal behavior.
- [ ] Provide a backend config value in `~/.config/hexen/launcher` from the selected Ansible variable; preserve safe Fuzzel fallback for helper use if the file is absent.
- [ ] Inspect task ordering and conditions to confirm invalid/missing Walker prerequisites fail before desktop package/config tasks.

### Task 3: Route launchers and menus through one dispatcher

**Files:**
- Modify: `config/bin/hexen-desktop`
- Modify: `config/hypr/bindings.lua`
- Modify: `config/waybar/config.jsonc`

**Interfaces:**
- Consumes: `~/.config/hexen/launcher` and CLI selection actions.
- Produces: backend-aware `launcher`, `dmenu`, `menu`, `system-menu`, and `clipboard` behavior.

- [ ] Add one helper function that invokes `fuzzel` or `walker` for application search and dmenu input, using fixed executable names only.
- [ ] Change Super+Space to call the helper's app-launch action; keep existing Super+Escape and menu routes, and route clipboard selection through the same dmenu helper.
- [ ] Preserve cancellation behavior and the existing explicit fixed action cases for lock, suspend, logout, restart, and shutdown.
- [ ] Keep Waybar's existing Hexen and battery callbacks backend-neutral by routing them through the helper.
- [ ] Review all launcher references with `rg` to ensure no user-facing shortcut or menu bypasses the dispatcher.

### Task 4: Add Walker config, theme, and session startup

**Files:**
- Create: `config/walker/config.toml`
- Create: `config/walker/themes/hexen/style.css`
- Create: `config/systemd/user/hexen-elephant.service`
- Modify: `config/hypr/hyprland.lua`
- Modify: `ansible/roles/desktop/defaults/main.yml`
- Modify: `ansible/roles/desktop/tasks/preflight.yml`
- Modify: `ansible/roles/desktop/tasks/main.yml`

**Interfaces:**
- Consumes: selected Walker backend and manually installed Elephant/provider packages.
- Produces: Tokyo Night themed Walker with desktopapplications as the default provider and prefixes for files, runner, calculator, and provider navigation; session startup launches Elephant and Walker only when selected.

- [ ] Configure Walker to use the repo-owned theme and only the selected providers; do not enable package install, clipboard, or Bluetooth integrations.
- [ ] Create a minimal user Elephant unit with `/usr/bin/elephant` as its service process and an appropriate restart policy.
- [ ] Link the single service file without linking over the user's entire systemd user directory; reload/start it only from the active user session after environment import.
- [ ] Start Walker's GApplication service from Hyprland startup only for the Walker selection.
- [ ] Review TOML, CSS, Lua, and unit text manually for valid key names, paths, ownership, and selected-provider consistency.

### Task 5: Update installation and behavior docs

**Files:**
- Modify: `install/README.md`
- Modify: `install/manual-apps/README.md`
- Modify: `docs/desktop.md`
- Modify: `docs/app-sources.md`
- Modify: `docs/resume.md`

**Interfaces:**
- Consumes: final install prompt, manual package procedure, and helper behavior.
- Produces: one end-to-end description of choosing and maintaining either backend.

- [ ] Document the default Fuzzel choice, Walker package prerequisite, supported provider integrations, package-source boundaries, and how rerunning provisioning changes the configured backend.
- [ ] Remove outdated claims that Walker is unavailable without explaining the reviewed manual option.
- [ ] Update shortcut/menu descriptions so they name the dispatcher behavior, not Fuzzel directly.
- [ ] Read the final docs alongside the spec and ensure they do not claim Walker packages are installed automatically or bit-for-bit reproducible.

