# Bitwarden Flatpak Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Install Bitwarden Desktop from Flathub as a repeatable part of Hexen provisioning.

**Architecture:** Add Flatpak to the official Arch app package list, manage the system Flathub remote and `com.bitwarden.desktop` through `community.general` modules, and document the source and update path. Validate in the disposable rehearsal VM without signing in.

**Tech Stack:** Ansible, Arch pacman, Flatpak/Flathub, Markdown.

**Spec:** `docs/superpowers/specs/2026-10-28-bitwarden-flatpak-design.md`

## Global Constraints

- Keep Flatpak installation system-wide and use the system Flathub remote.
- Install only `com.bitwarden.desktop` from Flathub.
- Do not sign into an account, import vault data, configure biometrics, enable autostart, or change browser extensions.
- Leave Flatpak update scheduling outside this change; document `flatpak update` as the separate app update path.
- Do not commit; the owner will make the final commit.

## Review Focus

- Provisioning on a fresh host: the remote must exist before the app install task.
- Existing Flatpak state: module tasks must be idempotent on a second run.
- Secret Service: rely on system `libsecret`/keyring support; never enter or store account credentials.
- Source identity: use the verified Bitwarden app ID `com.bitwarden.desktop`, not an unrelated community package.
- Desktop launch: verify the app reaches sign-in UI while leaving account setup to the owner.

---

### Task 1: Declare Bitwarden and verify it in the rehearsal VM

**Files:**
- Modify: `ansible/roles/apps/defaults/main.yml`
- Modify: `ansible/roles/apps/tasks/main.yml`
- Modify: `docs/app-sources.md`
- Modify: `install/manual-apps/README.md`
- Modify: `docs/operations-roadmap.md`
- Modify: `docs/resume.md`

**Interfaces:**
- Consumes: pinned `community.general` collection from `ansible/requirements.yml`.
- Produces: system Flatpak package, system `flathub` remote, and installed `com.bitwarden.desktop` app.

- [x] Add `flatpak` to `apps_packages`, which is installed from signed Arch repositories.
- [x] Add ordered `community.general.flatpak_remote` and `community.general.flatpak` tasks with `method: system`, the Flathub `.flatpakrepo` URL, and app ID `com.bitwarden.desktop`.
- [x] Update app source, manual install, roadmap and resume notes with the Flathub vendor verification, observed version, `flatpak update` path, keyring availability, and account-free scope.
- [x] Run the apps role in the VM and confirm Flatpak, the Flathub remote and Bitwarden install successfully (`ok=4 changed=2 failed=0`).
- [x] Launch Bitwarden in the VM and confirm its login screen appears; no credentials entered.
- [x] Run the apps role a second time and confirm zero changes (`ok=4 changed=0 failed=0`).
- [x] Run `git diff --check` and review the final diff; leave changes uncommitted.

**Acceptance limit:** the app's Flatpak metadata grants all devices and the app
could not create native-messaging sockets under the installed Zen profile.
Browser integration remains unaccepted. Final self-review performed by the
implementer; no fresh reviewer was used.
