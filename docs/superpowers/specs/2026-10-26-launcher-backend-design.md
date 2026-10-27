# Install-Time Launcher Backend Design

**Status:** Approved by owner on 2026-10-26.

## Intent

Let a new workstation choose Fuzzel or Walker during provisioning. Keep the same
Super+Space, Super+Esc, and Waybar entry points while making Walker's providers
available when Walker is selected.

## Goals

- Default to Fuzzel and install it from signed official Arch repositories.
- Offer Walker as an explicit install-time choice, using a reviewed, pinned
  package build path without an AUR helper or third-party pacman repository.
- Route the app launcher, system picker, Hexen menu, and clipboard picker through
  the selected backend.
- Keep selected backend, installed package set, deployed config, and session
  startup in agreement.
- Record package recipe revisions, upstream versions, source hashes, and manual
  update procedure.

## Non-goals

- Build or install AUR packages automatically from Ansible or the provisioner.
- Add Walker's package-search provider, AUR integration, Bluetooth controls, or
  clipboard-history provider by default. Existing cliphist remains the clipboard
  history implementation.
- Promise bit-for-bit reproducible binaries or freeze Arch's rolling system
  dependencies.

## Constraints and source review

The desktop role currently installs only official Arch packages. The project
keeps third-party builds manual and does not use an AUR helper. Preserve that
policy: Walker packages are built by the owner as an unprivileged user before
provisioning, with source verification and package-archive inspection, then
installed explicitly with pacman. Provisioning selects and configures a backend;
it does not fetch or execute package recipes.

The inspected AUR recipe commits use official upstream GitHub release archives
and fixed SHA-256 checksums. The recipes themselves are AUR community packaging,
not upstream-authored build files. Each inspected recipe contains only package
metadata, a Cargo or Go build, and staged installation of binaries/plugin files
and license/config assets; none has an install script. Pin these AUR recipe
commits and re-review recipe diffs and upstream source hashes before updating:

| Package | AUR recipe commit | Upstream release/source | SHA-256 |
| --- | --- | --- | --- |
| `walker` | `a801f3cc3be208a8cd188b2072087af1a413aecf` | Walker `v2.17.2` | `e50c606040b24f2a6045292f5f6a08c8a05ac599878ac781b1a5fcf50d353a56` |
| `elephant` | `fa4ae49703d0f1a2b47d3a93f0a373fb404aff39` | Elephant `v2.22.1` | `3d1d0d4c55ae531fa3f06406b96504b5165a0d7b53523d1f8351d9d93e457f44` |
| `elephant-desktopapplications` | `fec5937952dc3f320cef9741b401478aa26e5a57` | Elephant `v2.22.1` | same Elephant source archive |
| `elephant-files` | `2088f75f6ff637c339c55ec01a1bbd36ae6b8ffa` | Elephant `v2.22.1` | same Elephant source archive |
| `elephant-runner` | `01254600069cdadc8317af9416f50e3b68b7b76e` | Elephant `v2.22.1` | same Elephant source archive |
| `elephant-calc` | `5c2979c6790aeb19c686f19147e63e37b67c73ed` | Elephant `v2.22.1` | same Elephant source archive |
| `elephant-providerlist` | `96ce4305a7b8a217f348890fc66410af7cedec02` | Elephant `v2.22.1` | same Elephant source archive |

Walker selection requires those packages to be built and installed first. The
file provider depends on official `fd`; the calculator provider depends on
official `libqalculate`. The selected provider set gives Walker app search,
file browsing, command running, calculations, and provider navigation. Do not
install clipboard or package-management providers by default.

## Approaches considered

1. **Install-time choice (selected):** provision installs/configures only the
   selected launcher and routes shared entry points through it. Fuzzel stays the
   default. Walker's manually reviewed packages are a prerequisite for selecting
   it. This keeps package choices explicit and avoids duplicate launcher stacks.
2. **Runtime switch:** install both launchers and add a mutable setting. This is
   convenient for comparison but installs both stacks and makes package/config
   state easier to drift.
3. **Walker only:** use Walker for all installations. This gives the desired
   integration by default but removes the official-repository-only baseline.

## Proposed behavior

- `install/provision.sh` offers `fuzzel` or `walker` and defaults to `fuzzel`.
  It passes the selected value to Ansible; direct Ansible runs also default to
  Fuzzel and reject unknown values.
- Fuzzel selection installs the official `fuzzel` package, links its existing
  config, and starts it for application and dmenu pickers.
- Walker selection verifies the manually installed Walker, Elephant, and
  required provider files before system changes. It links a repo-owned Walker
  config/theme, starts Elephant and Walker in the user session, and routes the
  same application and dmenu actions through Walker.
- The user's selected launcher value is written into a small Hexen config file
  by Ansible. `hexen-desktop` reads that value, defaults safely to Fuzzel when
  absent, and uses a fixed executable/action mapping.
- Super+Space calls the Hexen launcher dispatcher. Super+Esc, the Hexen menu,
  Waybar, and the clipboard picker use the same backend-aware dmenu dispatcher.
- Documentation explains the manual Walker package build/install prerequisite,
  the selected source trust boundaries, and how to choose the backend on a fresh
  install.

## Approval boundary

Approval of this document authorizes implementation of the behavior above.
Package updates remain manual and require a new source/recipe review. The
provisioner will not build packages, change pacman repositories, import package
signing keys, or skip package/source integrity checks.
