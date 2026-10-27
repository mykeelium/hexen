# Reviewed manual application installation

The automatic playbook installs official Arch packages. Zen, 1Password, Zoom,
and Slack use reviewed manual builds. Their source/update details are in
[the application inventory](../../docs/app-sources.md). This keeps recipe and
signing-key decisions visible rather than hiding them in an AUR helper.

Walker is a separate optional desktop launcher. Its pinned manual recipe builds
for Walker, Elephant, and selected providers are documented in
[`walker/README.md`](walker/README.md). Build and install those packages before
choosing Walker in the provisioner; Ansible never builds AUR packages.
Fuzzel remains the default and comes from the official Arch repositories.
Walker uses the desktopapplications, files, runner, calc, and providerlist
integrations; it does not enable package search, AUR, Bluetooth, or clipboard
history. Existing cliphist continues to provide clipboard history.

The first VM run is recorded in
[validation-2026-10-26.json](validation-2026-10-26.json). Its artifact hashes
identify those exact inspected local builds. They are not upstream signatures,
version pins for all dependencies, or reproducible-build guarantees.

For another machine:

1. Read the inventory and inspect the exact current recipe, every referenced
   install script/patch/policy, its source URLs, integrity checks, and changes
   since the reviewed commit. Recheck official vendor instructions.
2. On a fully updated system, use a normal build account. For 1Password,
   download the vendor public key to a file, independently compare its primary
   fingerprint, and import only into that build user's GPG keyring. Never skip
   source/signature checks or change pacman's signature policy for these apps.
3. Run `makepkg --verifysource`, then resolve missing dependencies from official
   repositories. The VM needed mailcap, dbus-glib, ttf-dejavu, and libxss. Recheck
   dependencies on a fresh install rather than assuming this list is complete.
4. Build with `makepkg` without root. Inspect the resulting package metadata,
   archive paths/owners, setuid/setgid files, install script, Polkit policies,
   service/autostart files, and package hash before root installation.
5. Install the exact reviewed archive with `sudo pacman -U ACTUAL_PACKAGE`.
   Read transaction output. Verify installed ownership/integrity and launch it
   as the desktop user; rerun the main provisioner to check repeatability.

The inspected 1Password recipe derives Polkit owners from build-host accounts;
review this when moving a package between machines. Build per target unless
that policy has been deliberately reconciled. Its root-run install script
creates the helper group and sets BrowserSupport to root:onepassword 2755.
Do not add the desktop user to that helper group. Both 1Password and Slack
include a root-owned 4755 Chromium sandbox helper. Do not disable application
sandboxes to work around an untested launch.

The apps are now installed in the disposable VM. No AUR helper, third-party
pacman repository, Flatpak remote, or pacman signing key was added. The vendor
public key used for source verification lives only in the VM build user's GPG
keyring. Standard `pacman -Syu` does not update these manually built packages;
repeat source review, verification, build, and inspection for updates.

All four applications reached their expected welcome/sign-in windows in the VM.
Work-account sign-in and vault access remain owner actions and can be completed
on any computer. Installing the packages does not prove browser-extension or
meeting sharing works; no 1Password browser trust allowlist has been configured
and Zoom screen sharing still needs a live test.
