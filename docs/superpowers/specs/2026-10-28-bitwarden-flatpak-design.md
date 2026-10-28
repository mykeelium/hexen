# Bitwarden Flatpak design

## Intent

Add the Bitwarden desktop client alongside 1Password in the Hexen clean
installation. The owner selected Flathub after reviewing the available Linux
channels because the signed Arch package is stale. Install the vendor-verified
Flathub app; keep account sign-in and vault setup for the owner.

## Approaches

- **Flathub Flatpak (selected):** current vendor-verified desktop app with
  Flatpak process isolation. It adds the official Arch `flatpak` package and a
  system Flathub remote. Bitwarden's documented `libsecret` secure storage is
  already present through the GNOME keyring. The app remains updated through
  Flatpak, separately from pacman.
- **Arch `extra/bitwarden`:** native, signed pacman package with straightforward
  system integration, but it is flagged out of date and several releases behind
  upstream at this review.
- **Vendor standalone package:** avoids a new application repository, but its
  Linux package needs a manual update procedure and additional packaging work.

## Scope

- Declare Flatpak, the system Flathub remote, and `com.bitwarden.desktop` in
  Ansible so a clean provisioned system receives the same app.
- Record the source, version observed during VM acceptance, update path, and
  keyring/secure-storage requirements in the app inventory and install guide.
- Install and launch the app in the disposable rehearsal VM without entering
  account credentials or importing vault data.

## Non-goals

- Do not sign in, import/export vaults, change browser extensions, configure
  biometric unlock, enable autostart, or alter the VM's existing 1Password data.
- Do not add other Flatpak applications or change Flathub update scheduling.

## Acceptance

- The system package, system remote, and Bitwarden app are managed idempotently
  by Ansible; a second provisioning pass makes no changes.
- The installed app launches to its sign-in screen in the rehearsal VM.
- Secret Service is available to the app, and no account or credential is used
  during acceptance.
