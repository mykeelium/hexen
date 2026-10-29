# Graphical Login Implementation Plan

> **For agentic workers:** This plan is executed inline in the current session.

**Goal:** Provide a graphical, password-authenticated login that launches Hexen's Hyprland session without automatic login.

**Architecture:** Add Arch's SDDM display manager to the desktop Ansible role and enable its system service. Use SDDM's stock graphical greeter and the package-provided `hyprland-uwsm.desktop` session; do not configure autologin or Plymouth. Document LUKS unlock, account login, session selection, and console recovery as separate steps.

**Tech Stack:** Arch Linux, SDDM, systemd, Hyprland/UWSM, Ansible.

**Spec:** User request: graphical login, require manual account authentication, defer Plymouth.

## Global Constraints

- Preserve LUKS boot-time unlock and the existing account password.
- Do not configure automatic login.
- Leave Plymouth and initramfs/boot configuration unchanged.
- Do not replace or disable another display manager without explicit review.
- SDDM's greeter may use X11; the selected Hyprland desktop remains Wayland.

## Review Focus

- A second display manager must not be overwritten silently.
- The session list must include the existing UWSM-managed Hyprland entry.
- Failed greeter/session startup must leave a TTY recovery path.
- Enabling the manager must not silently run a package upgrade.

## Files

- Modify `ansible/roles/desktop/defaults/main.yml` and `tasks/main.yml` to install and enable SDDM.
- Modify `docs/desktop.md` and `docs/operations-roadmap.md` to document login behavior and acceptance.
- Modify `docs/resume.md` after VM deployment/acceptance.

## Tasks

- [x] Add SDDM to the reviewed desktop package set and enable `sddm.service` with autologin left unset.
- [x] Document the SDDM-to-Hyprland UWSM path, LUKS/account login boundary, and TTY fallback.
- [x] Install SDDM in the rehearsal VM from its current package database and enable it for the next boot. The package plan was six packages total (SDDM and five dependencies); no system upgrade was run.
- [ ] Reboot at a convenient time and confirm the graphical greeter, no automatic login, selectable UWSM Hyprland session, and successful password login. Reboot/visual acceptance remains pending so the live session is not interrupted.

## Verification

Use static syntax/diff checks on the source. VM acceptance consists of an SDDM login screen, manual account-password authentication, and a working Hyprland UWSM session. Do not run tests unless explicitly requested.
