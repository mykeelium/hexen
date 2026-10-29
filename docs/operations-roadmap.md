# Hexen workstation readiness and lifecycle roadmap

**Purpose:** track the remaining work to make this Arch setup safe to install on
the work computer, easy to maintain, and reproducible across the owner's
machines. This is a checklist and design direction; it does not mean every
listed feature must exist before the first laptop install.

**Current model:** install a standard Arch system with Archinstall, then apply
this repository with Ansible. This is not a custom Arch ISO. Keeping the
official installer and a reviewable post-install repository is simpler to
update and recover; a custom ISO can be a separate project if it becomes useful.

## What already exists

- [x] Archinstall choices and a Limine/LUKS2/Btrfs boot contract are documented.
- [x] `install/provision.sh` is the interactive post-install entry point; Ansible
  installs declared packages and configures the machine.
- [x] The system and desktop roles are intended to be repeatable. Configuration
  links point into the repository, and preflight checks refuse unmanaged files.
- [x] Common, desktop, and application package lists are declared in Ansible.
  Package sources and manual installation procedures are recorded separately.
- [x] Named themes, wallpaper-based Matugen packs, and the guided theme builder
  live with the desktop configuration.
- [x] The merged Neovim configuration and plugin pins are in the repository.
- [x] In the VM, root snapshot recovery was exercised from Arch media, including
  restoring the matching EFI files. Provisioning and configuration regression
  checks have also passed.
- [ ] A true upgrade to a newer kernel and the resulting reboot have not yet
  been proven. Recent desktop/theme changes also need a fresh VM acceptance pass.
- [ ] The documented snapshot procedure is not an off-machine backup. Home data,
  VM images, credentials, and recovery material need a separate backup plan.

## Priority 0: finish the pre-install gates

These are the current blockers to wiping the work computer.

- [x] **Rehearse a clean install from the official Arch ISO.** Completed on
  2026-10-27 using the 2026.10.01 ISO and Archinstall 4.5 on the disposable
  rehearsal disk. The owner confirmed encrypted Limine boot and login; initial
  `install/provision.sh --vm` completed with Fuzzel at source revision `d2a4f8d`.
  The separate clean-VM application and current-source acceptance gates below
  remain open. See [`machine choices`](../install/archinstall/choices.md).
- [ ] **Exercise a real full system upgrade.** From a pre-update root snapshot
  and matching `/boot` archive, install an actually newer kernel, reboot, unlock,
  and confirm Limine, initramfs, NetworkManager, audio, desktop, and the
  provisioner's zero-change rerun. Reinstalling the same package is useful
  evidence, but is not a substitute for this newer-kernel transition. On
  2026-10-28 the VM's repository had no newer kernel queued, and Arch's official
  [`linux` package page](https://archlinux.org/packages/core/x86_64/linux/)
  listed the same `7.2.11.arch1-1` version as installed in the VM.
- [ ] **Complete the laptop hardware inventory and live acceptance.** Identify
  GPU, Wi-Fi, Bluetooth, storage controller, firmware/UEFI behavior, camera,
  display layout/scaling, keyboard, touchpad, brightness keys, and suspend/resume.
  Test these on the target hardware; a VM cannot validate them.
- [ ] **Accept the real meeting workflow.** Pair the Bluetooth headset, complete
  a Zoom call, verify speaker/microphone/camera, share the whole Wayland desktop,
  and record/play back an OBS clip with the intended audio sources.
- [ ] **Verify work-account access and recovery.** Sign into the applications
  needed for work, confirm the FIDO authenticator and password manager work
  after a clean boot, and make sure account recovery does not depend on the old
  OS. Keep account tokens and private keys out of the repository.
- [ ] **Accept the owner's YubiKey and its recovery path.** On the target
  laptop, identify the key model and supported interfaces, verify browser
  FIDO2/WebAuthn and required work-account/password-manager authentication after
  a clean boot, and test a separately enrolled backup key or the account's
  independent recovery method. Record compatibility and procedures, not PINs,
  credentials, recovery codes, or enrollment files. Linux login/sudo and disk
  unlocking are separate opt-in work below; account acceptance does not prove
  those paths work.
- [ ] **Accept the Windows lab workload.** Create the required Windows VMs with
  virt-manager, check that memory/storage remain adequate for simultaneous
  guests, and verify the isolated libvirt network is not bridged to a work LAN.
- [ ] **Make and restore an independent data backup.** Confirm that personal
  files, existing VM disks, browser/editor data, SSH/GPG/FIDO recovery needs,
  and required work documents are copied somewhere other than this computer.
  Boot the recovery media and confirm the encryption passphrase and recovery
  instructions are available without relying on the machine being wiped.
- [ ] **Review the final package/source inventory.** Refresh the package and
  third-party source notes before installation. Keep signed Arch packages as
  the default. Explicitly decide which manually installed applications are
  required on the work computer and who updates them.
- [ ] **Complete application installation in the clean rehearsal VM.** Install
  and launch Zed, Zen, 1Password, Bitwarden, Zoom, Slack, and Hyprmon using
  their reviewed procedures. Confirm Zed launches with the selected Vulkan
  driver. Install matching Walker/Elephant/provider builds if Walker is the
  selected launcher, and test app search, calculations, and Google fallback.
  Verify normal/private browser shortcuts and required desktop entries. Evidence
  from the older acceptance VM does not complete this clean-VM gate; account
  sign-in remains an owner action. On 2026-10-28, the separate clean rehearsal
  VM built and installed Walker 2.17.2 with all seven Elephant 2.22.1 providers
  from the pinned commits in `install/manual-apps/walker/sources.lock`.
  Provisioning selected Walker successfully; the GUI opened, and direct
  provider queries returned an app match, `1+1` -> `2`, and the configured
  Google search action. This verifies Walker's component of the gate. Zen
  Browser 1.23.4b-1 was built from its reviewed recipe and installed; the
  Google test URL is now visible in the running Zen window. The VM also built
  and installed 1Password 8.12.42-36, Zoom 7.2.1-1, and Slack 4.52.182-1 from
  their inspected local packages. Slack displayed its sign-in screen and Zoom
  initially displayed its Workplace window; no account was signed in. During
  the later unlocked visual check, a Zoom “quit unexpectedly” report appeared
  over the Workplace window. Its saved crash record shows SIGSEGV in Zoom while
  calling GLib's spawn helper; a Workplace window currently runs after relaunch,
  but the cause is unresolved. The 1Password launch first presented its Crash
  Reporter window. A later diagnostic launch with `--disable-gpu` reached the
  normal welcome window, which suggests a VM graphics-path interaction but
  does not prove the cause. Verify normal GPU-enabled launch on hardware. The
  GNOME keyring service is
  active, and the user created the keyring. `pacman -Qkk` found no changed files
  in Zoom, Slack, Zed, or Zen; 1Password's only difference is its expected
  BrowserSupport group/mode change from its reviewed install script.
  Hyprmon was built at the pinned commit, its upstream Go tests passed, and its
  display-settings TUI opened in Ghostty. Its monitor save/apply action remains
  untested to avoid changing the VM display layout. Zed opens, but reports
  software-emulated llvmpipe rather than using the selected `vulkan-virtio`
  driver; the VM's virtio video has no 3D acceleration enabled. Resolve or
  explicitly scope this VM limitation before accepting the Zed GPU criterion.
  App launch evidence does not complete the application gate: verify the
  1Password normal GPU-enabled launch, resolve Zed's Vulkan acceptance, verify
  Walker's normal and private browser shortcuts, and complete the account-free
  post-reboot checks. The deployed private-browser helper opened a Zen private
  window and Hyprland reports the browser bindings loaded; the actual keypress
  and private browsing behavior remain untested. See the app-source notes.
  Bitwarden Desktop 2026.10.0 was installed from the Bitwarden-verified Flathub
  listing; its login screen opened without sign-in. The second apps-role run
  reported zero changes. Its Flatpak permissions and keyring availability were
  inspected; native messaging with Zen remains unverified.
- [ ] **Converge the VM onto one reviewed source revision.** Reconcile the
  VM-local lock-screen change with the development checkout, review the pending
  desktop/Starship changes, and deploy a recorded Git checkpoint. On 2026-10-28
  both checkouts advanced to `382de1c`; the former VM branch and its pre-deploy
  diff are retained in the VM recovery directory. Lock-screen, Walker, Starship,
  Waybar, and desktop-helper sources match the host checkout. The VM selects
  Walker, its managed config links resolve into `/home/mcuomo/hexen`, its active
  generated theme is `gruvbox-dark`, and Elephant is active. The full VM-mode
  Ansible playbook ran twice with `changed=0`, `failed=0`; PipeWire and
  WirePlumber are active and no failed system units were reported. A normal
  reboot, login and lock/unlock check, required-app launch checks, and audio or
  capture acceptance remain. VM-mode provisioning disables nested libvirt
  network management because its default `192.168.122.0/24` overlaps the VM's
  own `enp1s0` subnet; this VM has not accepted guest networking. Keep each
  machine's deployment separate so VM provisioning cannot alter the host.
- [ ] **Accept the maintenance and firewall baseline below.** Package presence
  alone does not complete this gate: prove the configured services, firewall
  behavior, snapshot retention, and backup restore workflow in the VM first.
- [ ] **Capture a clean repository checkpoint.** Review `git status`, commit or
  intentionally retain the completed setup work, and make sure no credentials,
  local VM files, private wallpapers, or machine-specific secrets are tracked.

## Priority 0: complete the requested maintenance packages

The owner requested the following additions after the 2026-10-28 readiness
audit. These are accepted scope, not suggestions awaiting another package
selection. Implement them through the declared package/service configuration;
leave each item unchecked until its configuration and acceptance checks pass.
Physical-device acceptance remains deferred until the hardware phase.

- [x] **Accept `pacman-contrib` and its configuration/cache workflow.** The
  package is declared for installation. The weekly `paccache.timer` is configured
  to retain its default three versions per package; `pacdiff` remains a manual
  review step for `.pacnew`/`.pacsave` files. In the rehearsal VM,
  `pacman-contrib` 1.13.1-1 and `pacdiff` are installed; `paccache.timer` is
  enabled and active with a weekly schedule, and the packaged service invokes
  `paccache -r` with its default keep-three behavior. `paccache --dryrun --keep
  3` reported no eligible cache entries. The documentation's dry-run command
  was corrected after the old form returned “only one operation may be used at
  a time.”
- [ ] **Configure and accept independent `restic` backups.** The package is
  declared for installation; no destination or credentials are assumed. Choose
  an off-device destination, encrypted repository, schedule, exclusions,
  retention, and failure reporting. Keep repository credentials outside Git and
  make them recoverable independently of the machine. Define a consistent
  backup method for VM disks; copying an actively changing image is not
  sufficient acceptance. Restore representative files and a VM image into a
  separate destination and verify permissions and usability. See the
  [restore procedure](https://restic.readthedocs.io/en/stable/050_restore.html).
- [ ] **Accept the initial `firewalld` baseline and complete the policy below.**
  The package and service are declared, with a persistent and runtime `drop`
  default zone so unknown NetworkManager profiles start untrusted. Verify
  effective policy and conflicts in the rehearsal VM, then complete the
  connection, LocalSend, libvirt, VPN, and external IPv4/IPv6 tests in the next
  section. The 2026-10-28 VM audit found firewalld active/enabled, nftables and
  UFW services inactive, `drop` as both defaults, and `enp1s0` in the active
  `drop` zone. No listening sockets were reported. It also found the packaged
  `drop` zone had intra-zone forwarding enabled; the base role now owns a local
  fail-closed zone definition that does not enable it. The targeted Ansible run
  installed the policy and reloaded firewalld; a second run reported
  `changed=0`. Runtime and permanent queries both report target `DROP`, only
  `dhcpv6-client`, and `forward=no`; the built-in IPv6 host policy is active,
  and DNS plus IPv4 HTTPS still work. The VM has no IPv6 default route. Custom
  trust mapping, VM/VPN forwarding, trusted-profile behavior, and external
  IPv4/IPv6 probes remain unaccepted.
- [ ] **Accept `fwupd` for firmware maintenance.** The package is declared; no
  firmware update is run automatically. Inspect supported devices and available
  firmware on the physical machine. Document the update/recovery procedure;
  firmware writes and associated reboots remain explicit owner actions rather
  than part of routine unattended provisioning.
- [ ] **Accept `smartmontools` for physical drive health.** The package is
  declared. Verify supported drive health reporting on physical hardware, choose
  useful monitoring/notification settings, and document how to inspect a warning.
  A virtual disk cannot validate physical SMART data.
- [ ] **Accept `power-profiles-daemon` for laptop power profiles.** Its package
  and service are declared. Confirm supported profiles, AC/battery transitions,
  thermals, suspend/resume, and desktop integration on the laptop. Reconcile any
  existing power-management policy before hardware acceptance.
- [ ] **Verify CPU-specific microcode and the hardware package profile.** Select
  `intel-ucode` or `amd-ucode` as appropriate, verify its boot integration, and
  record GPU/Wi-Fi firmware and driver requirements. Absence in a virtual guest
  is not evidence that a physical machine can omit these checks.
- [x] **Accept Snapper snapshot cleanup.** Snapper creates no automatic timeline
  snapshots. Cleanup-managed disposable snapshots are bounded by count and age;
  update recovery checkpoints and matching `/boot` archives have no cleanup tag
  and remain manual-retention pairs. In the rehearsal VM, the active cleanup
  timer and installed 7-day/10-and-5 policy matched the source template. A
  disposable test created three `number` snapshots with temporary 1-second/two
  snapshot limits; cleanup removed the oldest and retained the newest two while
  preserving all existing recovery snapshots. The original policy was restored
  and all test artifacts were removed.
- [ ] **Review SSD trim policy on physical hardware.** `fstrim.timer` remains
  disabled until the physical LUKS/Btrfs layout and discard/privacy tradeoff are
  reviewed.

## Priority 0: implement and accept a robust workstation firewall

The initial VM audit found nftables installed but no firewall policy loaded.
Firewalld now runs and owns an nftables table with a repository-managed `drop`
zone as default. Its untrusted policy has no intra-zone forwarding. Remaining
work is to bind any trust to selected NetworkManager profiles, define scoped
workflow exceptions after those profiles are known, and test from another
machine. VM acceptance comes first; the target laptop's network and hardware
checks can follow later.

- [x] **Define the baseline and its ownership.** The base role owns the
  `/etc/firewalld/zones/drop.xml` policy. It uses target `DROP`, permits only
  `dhcpv6-client`, and defines no ports, rich rules, or intra-zone forwarding.
  Runtime and permanent VM state match, firewalld's `allow-host-ipv6` policy is
  active, and DNS plus IPv4 HTTPS remained functional after reload. External
  IPv4/IPv6 filtering is still covered by the separate cross-machine test below.
  The baseline denies unsolicited inbound traffic for IPv4 and IPv6, allows
  established/related traffic and ordinary outbound client use, and restricts
  forwarding to explicitly required VM/container networks. Keep loopback and
  essential DHCP, DNS responses, ICMP/ICMPv6, and IPv6 neighbor-discovery
  behavior functional. Inspect effective service allowances rather than
  assuming a named default zone is sufficient;
  inbound SSH and other remote-management services require an explicit need.
- [ ] **Bind trust to NetworkManager connection profiles.** New or unknown
  networks must use the untrusted policy. Assign trusted LAN exceptions only
  to owner-selected connections; do not trust every private-address subnet.
  Verify Ethernet/Wi-Fi changes, reconnects, renamed interfaces, and firewall
  restarts. The 2026-10-28 VM check found its saved wired profile has no explicit
  zone, while active `enp1s0` uses the default `drop` zone; no trusted exception
  is assigned. Firewalld is enabled and active. There is no Wi-Fi profile in
  this VM; reconnect and renamed-interface behavior remain untested. See
  [NetworkManager/firewalld zone assignment](https://firewalld.org/documentation/zone/connections-interfaces-and-sources.html).
- [ ] **Scope LocalSend and discovery exceptions.** Record the actual discovery
  and transfer requirements, allow them on selected trusted networks, and test
  transfers in both directions. Verify they remain unavailable through the
  untrusted profile; avoid a broad all-ports or all-multicast exception. The VM
  has no LocalSend package or UDP listeners, and the untrusted zone has no
  discovery allowances. This confirms the current fail-closed behavior; keep
  transfer acceptance open until a concrete workflow and trusted profile are
  selected.
- [ ] **Preserve isolated virtualization networking.** Validate libvirt guest
  DHCP/DNS, outbound NAT, and the Windows lab's required isolation. Scope host
  service allowances to the virtual bridge and required services, keep guests
  off the physical work LAN unless deliberately configured, and test rootless
  Podman separately. Preserve libvirt-managed networking rules; do not flush
  unrelated tables to apply the workstation policy. See [libvirt firewall integration](https://libvirt.org/firewall.html).
  The rehearsal VM's libvirt services are disabled and its default network is
  inactive; starting it would overlap the VM's own `192.168.122.0/24` subnet.
  Podman reports rootless mode with `netavark`, but container connectivity has
  not been exercised. DHCP/DNS/NAT/isolation and container firewall behavior
  remain open for a non-nested VM or the physical machine.
- [ ] **Accept VPN behavior deliberately.** Test OpenVPN connection,
  disconnection, reconnect, DNS, IPv4/IPv6 routes, and interaction with LAN/VM
  exceptions. Define whether an optional VPN kill switch is needed and what it
  protects; a normal workstation firewall is not proof of a kill switch or
  leak-free VPN routing. On 2026-10-28 the VM had `openvpn` and
  `networkmanager-openvpn` installed but no VPN connection profile; no provider
  configuration or credentials are present, so connection and kill-switch
  behavior cannot be tested here.
- [ ] **Prove persistence and repeatability.** Enable the firewall for boot,
  verify the policy is effective after reboot and reload, and reconcile runtime
  versus permanent rules. A second provisioning run must make zero changes.
  Missing service/policy, unexpected zone membership, or unintended listening
  services must be visible in the readiness report. Firewalld is enabled and
  active in the VM. After a reload on 2026-10-28, runtime and permanent defaults
  were both `drop`, both policies allowed only `dhcpv6-client` with forwarding
  disabled, and HTTPS to archlinux.org returned 200. Two earlier full VM-mode
  provisioning runs reported zero changes; post-reboot policy verification
  remains open because reboot requires unlocking the encrypted VM at its
  console.
- [ ] **Test from another disposable machine.** Verify expected allowed and
  blocked connections over both IPv4 and IPv6, including unsolicited inbound
  traffic and VM forwarding. Also test browsing, package downloads, DNS/NTP,
  LocalSend, VPN use, and required meeting/capture workflows. Record expected
  results and observed results; a local connectivity test alone is insufficient.
  On 2026-10-28 a temporary listener on the VM's IPv4 interface timed out when
  probed from the development host; it was stopped and no listener remained.
  This preliminary local-peer check is consistent with inbound filtering, but
  the required separate disposable peer, IPv6, forwarding, and workflow tests
  remain open.
- [ ] **Document diagnostics and local-console recovery.** Provide commands to
  inspect zones, effective rules, listeners, and rate-limited local drop logs.
  Keep logs bounded and avoid recording payloads or uploading them automatically.
  Back up the known-working policy and test restoring it from a local console.
  A failed rule deployment must report failure and retain or restore the last
  working policy rather than silently opening the firewall. Diagnostics and a
  local-console recovery procedure are now documented in
  [`maintenance`](maintenance.md); the recovery procedure has not been exercised,
  and the baseline intentionally has no drop-logging rule yet.

## Deferred: opt-in remote control of the active desktop

- [ ] **Deploy and accept the SSH-tunneled WayVNC workflow.** The code, helper,
  and [guide](remote-desktop.md) are retained, but workstation provisioning
  leaves remote access disabled by default. When explicitly opted in,
  provisioning installs OpenSSH and WayVNC and links the on-demand
  `hexen-remote start|stop|status` helper and user service. The
  `hexen-remote-client <ssh-destination>` command starts the service over SSH,
  creates the tunnel, opens the viewer, and cleans up when it closes. WayVNC
  binds to loopback and is never started automatically. The guide covers SSH
  key setup, host-key verification, and a firewall exception scoped to the
  remote client's source address; `sshd` and firewall access still require
  deliberate setup. A separate Hyprland compositor launched over SSH could
  not acquire a seat.

  Rehearsal evidence: in the active logged-in session, the one-command wrapper
  started WayVNC, opened the SSH tunnel, received 1280x800 framebuffer metadata,
  sent pointer input, and stopped WayVNC and the tunnel when the test viewer
  exited. A real viewer also connected and remote pointer input moved the VM
  cursor. Rendered pixels, lock-screen access, and multi-monitor behavior remain
  unverified, so keep this gate open.

  Parked VM state (2026-10-29): `sshd` is disabled and inactive; its permanent
  and runtime firewalld exception was removed; the ignored source override is
  empty. No listener is bound to port 22. The VM checkout, helper, service,
  host-key pin, key, client alias, and installed WayVNC package remain as
  rehearsal artifacts for later reactivation. Revalidate before reactivating.

  Before acceptance, confirm the client sees the intended display layout, can
  open its own applications and files, can connect to the lock screen, and loses
  access when the WayVNC service is stopped. Do not add a public VNC listener or
  enable SSH automatically.

## Priority 1: make configuration changes easy to manage and distribute

The repository already is the central source for the configs it manages: the
desktop role links files from the clone, so editing a linked file edits the
repository copy. Git history is the distribution mechanism. The missing part is
a clear day-to-day workflow and explicit machine profiles.

- [x] **Keep one source of truth initially.** This Git repo holds the
  Archinstall notes, Ansible roles, common desktop configs, themes, scripts, and
  docs. Ansible manages system packages/services and deploys configuration;
  Git reviews and distributes edits. The current setup has no second dotfile
  engine, so retain this model unless the workflow demonstrates a limitation.
- [x] **Define software profile layering.** Shared packages remain common;
  selected `common`, `numen`, or `arcana` profiles can add packages, followed
  by ignored per-machine package additions. The tracked profile lists are empty
  until software differences are chosen. Credentials remain outside Git. See
  [`machine profiles`](machine-profiles.md).
- [ ] **Add hardware profile settings.** After identifying the machines, add
  monitor/GPU/input/network choices as small overrides instead of duplicating
  common config trees. Keep these settings and private machine data out of the
  common layer; validate them on the actual hardware.
- [x] **Add `hexen config status` and `diff`.** These read-only commands report
  the selected profile, repository revision/dirty state, managed desktop links,
  and staged, unstaged, or untracked repository edits. See
  [`machine profiles`](machine-profiles.md).
- [x] **Add `hexen config apply`.** It delegates to the existing interactive
  provisioner, which shows its impact summary, asks before proceeding, checks
  Ansible syntax, and retains the desktop role's unmanaged-file protections.
  `--vm` forwards the nested-VM network mode.
- [x] **Add `hexen config backup`.** It makes a new private, timestamped copy
  of a file or directory under `~/.config/` or the repository's `config/` tree.
  It refuses paths outside those trees and never replaces an existing backup.
- [x] **Add safe config restore.** It accepts only an identified backup,
  requires interactive confirmation, restricts the destination to the original
  config tree, and creates a safety backup before replacing an existing path.
  Symlinked destinations and type mismatches are refused.
- [x] **Document the edit-and-share loop.** The machine profile guide now
  covers editing through links or in the repository, reviewing staged/unstaged
  and untracked changes, validating the relevant config, staging only reviewed
  files, committing, and fast-forwarding another machine to the reviewed
  revision. It also distinguishes common settings, tracked profile package
  additions, and ignored machine-local values.
- [x] **Keep Git and Ansible as the config workflow for now; defer chezmoi.**
  This remains an Arch-only setup with Ansible-managed system configuration and
  Git-managed desktop files. The current scope has not demonstrated a need for
  another dotfile engine. Reconsider only if the project grows to many more
  home-directory files, multiple operating systems, or templated secret
  handling.

## Priority 1: add opt-in YubiKey authentication

Treat the YubiKey as several authentication integrations with separate enrollment
and recovery requirements. Begin with browser/work-account acceptance above;
do not make a working base install depend on a key being present.

- [ ] **Define the intended uses and hardware compatibility.** Record which
  keys support the requested FIDO2/WebAuthn, SSH security-key, PIV, OpenPGP, or
  OATH features; include only the uses the owner needs. Review official Arch
  packages, USB permissions, and any required smart-card service for those uses.
  Provisioning must not reset a key, change its PIN, overwrite credentials, or
  enroll it unattended. Keep device-specific enrollment data outside Git.
- [ ] **Design Linux login, sudo, and desktop authorization deliberately.**
  Decide which of TTY login, sudo, Polkit, and Hyprlock should use the key, and
  whether each requires password plus touch/PIN or supports a passwordless mode.
  Review the actual PAM stack for each service using
  [Yubico's pam-u2f documentation](https://developers.yubico.com/pam-u2f/).
  Keep enrollment interactive and enabling PAM integration explicitly opt-in.
- [ ] **Prove recovery before enforcing key authentication.** Enroll and test a
  second key where supported, define how lost-key recovery is authorized, and
  preserve a tested administrative/recovery route. Test correct and wrong PINs,
  missing/unregistered keys, touch timeout, screen unlock, suspend/resume, cold
  boot, and deliberate recovery. A normal authentication failure must not
  silently bypass the chosen policy. Validate on the target laptop; a VM without
  the actual key cannot accept the physical-device workflow.
- [ ] **Evaluate FIDO2 disk unlocking as a separate boot project.** The current
  validated boot path uses mkinitcpio's `encrypt` hook. Review a compatible
  token-unlock design before changing that contract; enrollment alone is not a
  proven boot path. If adopting
  [systemd-cryptenroll](https://www.freedesktop.org/software/systemd/man/latest/systemd-cryptenroll.html),
  validate the corresponding initramfs/unlock integration in a disposable VM
  and then on hardware. Retain an independent LUKS passphrase/recovery method,
  protect an appropriate header backup, and test boot/recovery with the key
  absent. Do not remove working passphrase slots as a provisioning step.
- [ ] **Document daily use and replacement.** Cover enrollment, backup-key
  registration, replacement/revocation, PIN retry behavior, account recovery,
  and how to restore the chosen PAM/boot configuration. Implement read-only
  diagnostics before offering any enrollment or authentication-policy changes.

## Priority 1: complete the desktop capture workflow

Hexen currently binds Print to a `grim`/`slurp` region capture copied to the
clipboard. The owner wants a more complete screenshot workflow inspired by
[Omarchy's capture flow](https://omarchy.baris.sh/manual/screenshots-recording/).

- [x] **Implement the local screenshot flow in source.** Print captures a region;
  Super+Shift+Print offers region, current-workspace window, focused-display,
  and annotated-region capture. Every completed image is saved to
  `~/Pictures/Screenshots` and copied to the clipboard. The desktop role installs
  Swappy for annotation and links its config. See [desktop guide](desktop.md).
- [ ] **Accept the flow in the rehearsal VM.** Check that all four menu choices
  work, the saved images open, clipboard paste works, and cancellation leaves no
  stray partial file. Record any needed fixes here before the laptop install.

## Priority 1: provide a graphical account login

- [x] **Add a password-authenticated graphical login.** The desktop role
  installs SDDM and enables its service without configuring automatic login.
  The existing LUKS unlock remains separate from account login. The selected
  session is **Hyprland (UWSM-managed)**; Plymouth and boot-splash changes are
  deferred. See the [desktop guide](desktop.md#graphical-login).
- [ ] **Accept graphical login in the rehearsal VM.** After the next planned
  reboot, confirm the SDDM greeter appears, automatic login is off, the
  UWSM-managed Hyprland session is selectable, and account-password sign-in
  starts the expected desktop. Keep TTY recovery available and record any
  greeter or session errors before considering this complete.

## Priority 1: add a safe, single update entry point

Today, `pacman -Syu`, Git updates, Ansible provisioning, Neovim tools, and manual
application updates are separate procedures. A future `hexen update` should
coordinate the supported work and leave source changes reviewable. Omarchy's
current `omarchy update` is a useful reference for coordinating logs, locking,
space checks, snapshots, package updates, migrations, restarts, boot checks,
and reboot prompts in one visible workflow ([update process](https://github.com/omacom/omarchy/blob/quattro/docs/update-process.md),
[user guide](https://github.com/omacom/omarchy/blob/quattro/manual/30-updates.md)).
Hexen should use the parts that fit this setup; it should not automatically
build AUR packages or run unreviewed remote scripts.

- [x] **Implement `hexen update --check` in source.** It reports local Git
  changes and cached upstream divergence, official package updates from the
  local sync database, a limited kernel reboot signal, and managed config-link
  drift. It does not fetch, refresh package databases, or modify files. See
  [machine profiles](machine-profiles.md#checking-update-status).
- [ ] **Accept `hexen update --check` in the rehearsal VM.** Confirm output and
  exit behavior for clean/dirty/diverged repositories, stale package data,
  pending packages, kernel mismatch, and config-link drift.
  A read-only invocation on the development host (2026-10-29) exposed that
  `pacman -Qu` returns status 1 with no output when it lists no updates; Hexen
  now reports that case as “none listed.” The sync database was stale, so this
  host run does not establish update availability. The system and session
  libvirt lists were empty, leaving the VM acceptance pass open.
- [x] **Implement the checkpointed Arch package-update slice.** `hexen update`
  requires a TTY, clean checkout, explicit source review for incoming upstream
  commits, supported Btrfs/Snapper/ESP layout with separate `/home`, adequate
  archive and `/boot` working space, and no existing Pacman lock. It starts a
  private log, then asks before
  recording package and mount manifests, creating a permanent root snapshot and
  matching `/boot` archive, and running one `pacman -Syu`. It records package
  results, `.pacnew`/`.pacsave` candidates, failed system units, and a limited
  kernel reboot signal. It never reboots. See
  [update status and recovery boundaries](machine-profiles.md#checking-update-status).
- [x] **Review and fast-forward source explicitly.** The interactive updater
  fetches the configured remote, stops on divergence, displays incoming commits
  and the full diff, and asks before a clean fast-forward. It records both
  revisions because source-linked home config is outside the root snapshot.
- [x] **Offer reviewed Ansible convergence after the system update.** The
  updater asks separately after package/migration inspection. Provisioner review
  mode shows an advisory Ansible check/diff and requires another confirmation
  before applying; VM network settings require `hexen update --vm`. It records
  the result, post-convergence package manifest, and failed units. VM acceptance
  remains open.
- [x] **Add source-specific local checks and service-restart guidance.** The
  source report checks the LocalSend pinned digest, local app/package presence,
  Bitwarden's installed Flatpak version, Hyprmon's binary presence, and Neovim's
  tracked pin count; it makes no claim about upstream freshness. When available,
  `checkservices -P` skips `pacdiff` and asks before each service restart. The
  base role now installs `archlinux-contrib` for this tool. No restart is
  automatic.
- [ ] **Accept the checkpointed update in the rehearsal VM.** Exercise cancel,
  fetch failure, source-update decline/accept, clean fast-forward and divergence,
  successful and failed Pacman transactions, checkpoint completeness, low-space
  and lock refusal, post-update records, and manual recovery from the paired
  root snapshot and `/boot` archive. Exercise migration and convergence cancel,
  preview, apply, failure, and post-convergence reporting. Use a newer kernel
  when one is available. Check source-report findings and `checkservices` with
  both declined and accepted service restarts.
- [x] **Define rollback boundaries in the update UI and guide.** The root
  snapshot excludes `/home`; restore `/boot` only from its matching archive.
  Restore repo-managed user config from a reviewed Git revision and reapply it;
  restore personal files from a separate backup. The local recovery pair is not
  an off-device backup.
- [x] **Keep safe exits simple.** No ALPM guard was added, so normal Pacman use
  remains available outside Hexen's own update lock. The direct package-manager
  and offline recovery routes remain documented. Revisit recovery shells,
  unattended maintenance, Ansible, and package-manager frontends before ever
  considering a system-wide guard.
- [x] **Separate update ownership.** The
  [application source guide](app-sources.md#update-ownership) names the owner
  and procedure for signed Arch packages, Flatpak, AUR/vendor packages, Walker
  and Elephant, Hyprmon, LocalSend, Neovim plugins/parsers, and Mason tools. It
  makes clear which updates are manual or separate from Pacman and does not
  imply unsupported sources are covered by `hexen update`.
- [x] **Add a migration mechanism before changing user data automatically.**
  `hexen migrate` runs reviewed, numbered Python migrations from
  `install/migrations/manifest.json` as the current user. Private per-user
  markers are written atomically only after success; failed work stays pending
  and logs are retained under Hexen's state directory. `hexen update` offers
  pending migrations after Pacman succeeds and the package manifest is saved.
  They never run in the package transaction or as root. The registry is empty
  until a concrete user-data migration is reviewed and added. VM acceptance of
  successful, failed, declined, and resumed migration flows remains open.
- [x] **Add scheduled Arch package discovery and daily notifications.** Use a
  persistent, non-root user timer to refresh an isolated package database with
  [`checkupdates`](https://man.archlinux.org/man/extra/pacman-contrib/checkupdates.8.en).
  Do not install updates or refresh Pacman's system sync database. When updates
  are available, send a daily digest with package names, installed and candidate
  versions, repository, check time, and a link to a full report. Make offline,
  stale-metadata, and check-failure states explicit instead of reporting “up to
  date.” The notification action should open the report or a terminal running
  `hexen update`; it must never start a privileged update silently. The
  `hexen update-monitor` command and persistent user timer write private reports
  under `~/.local/state/hexen/updates/`; VM acceptance remains open.
- [x] **Create the initial Arch package provenance and change inventory.** For
  installed package changes, retain old/new versions, the Pacman repository and
  signature transcript, package metadata and `.BUILDINFO` when cached artifacts
  are available, and a file inventory/diff when both artifacts are available.
  Link official packages to their Arch package page and packaging Git history.
  Arch's [build system](https://wiki.archlinux.org/title/Arch_Build_System)
  stores build recipes separately from upstream source, and package archives can
  contain `.BUILDINFO` metadata ([package format](https://wiki.archlinux.org/title/Creating_packages)).
  A valid signature establishes the trusted signer for that artifact, not that
  the source or build is harmless ([package-signing model](https://wiki.archlinux.org/title/Pacman/Package_signing)).
- [ ] **Extend provenance coverage beyond Arch packages.** Link AUR packages to
  the reviewed PKGBUILD revision and source checksum/signature evidence; review
  Flatpak, vendor packages, AppImages, Walker/Elephant, Neovim plugins, and
  language tools source by source. Do not imply Pacman covers them. Treat
  missing provenance or unavailable old artifacts as “not compared,” never as a
  clean security result.
- [x] **Record update-monitoring evidence for the work profile.** Keep private
  timestamps, findings, notifications, and the owner's review/apply/decline
  decision so scheduled discovery and response can be demonstrated. Confirm
  with the employer that scheduled detection plus owner-approved installation
  satisfies its “automatic updates” requirement; do not describe this opt-in
  flow as unattended installation if the policy requires that. Employer-policy
  acceptance and VM workflow acceptance remain open.
- [x] **Implement an interactive, package-by-package update review in source.**
  `hexen update-monitor review` presents each candidate's installed and
  candidate version, repository, Arch package page, and recipe history. The
  owner can record reviewed, wanted, follow-up, or undecided status in the
  private evidence log; decisions persist as they are made. A final summary
  offers an explicit handoff to the existing checkpointed `hexen update`
  workflow or cancellation. A richer TUI can build on the independent review
  state and evidence functions without adding a dependency to this first
  terminal interface. **Rehearsal-VM acceptance remains open.** Flags record
  intent; they never filter the system transaction. Arch requires a full
  system upgrade after refreshing repository databases, and partial upgrades
  are unsupported ([ArchWiki guidance](https://wiki.archlinux.org/title/System_maintenance#Partial_upgrades_are_unsupported)).

## Priority 2: operational resilience and maintenance

- [ ] **Add `hexen doctor`.** Read-only report for Arch release, repo revision
  and dirty state, profile, broken config links, package differences, active
  critical services, failed units, disk space, snapshots, boot artifacts,
  network, and pending migrations. Include missing manual applications and
  launcher providers, source-versus-deployed revision drift, snapshot cleanup
  status, firewall policy/zone state, backup freshness, and pending firmware
  work. Support a privacy-reviewed report file; do not upload logs automatically.
- [ ] **Create an off-device backup policy.** Snapshots protect against local
  rollback mistakes, not drive failure, theft, or accidental deletion. Define
  encrypted backup destinations and retention for home files, editor data,
  VM images, and recovery material. Test restoring representative files.
- [ ] **Finish boot rollback instructions.** The existing documented recovery
  restored a matching snapshot and ESP archive. The repair path when the saved
  boot archive is missing or inconsistent remains unvalidated; prove it in a
  disposable VM before automating any boot repair.
- [ ] **Track `.pacnew` and `.pacsave` files.** Report candidates after updates,
  show diffs, and let the owner merge them. Never replace an edited config
  automatically.
- [ ] **Decide firmware maintenance.** Document when to inspect LVFS/fwupd and
  laptop-vendor firmware, keep firmware separate from routine package updates,
  and require an explicit user action for firmware writes/reboots.
- [ ] **Add recovery-friendly package records.** Save package manifest, repo
  revision, profile, update log, boot hashes, and snapshot number together for
  each successful system update. Keep secrets and private config contents out
  of the record.
- [ ] **Set an upstream review cadence.** Recheck source URLs, signatures,
  checksums, AUR recipes, and out-of-date official package flags before
  changing their automation. Keep pinned third-party builds manual until the
  review/update path is reproducible and trusted.
- [ ] **Harden and refine remote desktop later.** After the current SSH-tunneled
  WayVNC workflow is fully accepted, revisit it as a separate quality pass:
  verify the rendered image, lock/unlock behavior, multiple monitors, reconnects
  after network or suspend changes, and cleanup after client or server crashes.
  Improve the client command's status and error messages, document host-key and
  firewall changes, and decide whether a dedicated desktop-client package or
  menu entry is useful. Keep VNC loopback-only and remote access opt-in.

## Suggested delivery order

1. Complete the clean-VM applications, reviewed-revision deployment, requested
   maintenance packages, firewall acceptance, snapshot retention, and backup
   restore gates. Keep physical hardware acceptance deferred until that phase
   is resumed; it still must pass before replacing the work computer's OS.
2. Add common/numen/arcana profile selection and the Git-based config status/diff
   workflow.
3. Build and exercise `hexen update --check`, then the logged, locked,
   snapshot-backed update path in the disposable VM.
4. Add idempotent migrations, `.pacnew` reporting, and `hexen doctor` as the
   update path exposes real needs.
5. Add the Waybar/menu update indicator and decide whether a broader dotfile
   manager or firmware helper is justified.
6. Only then install on the work computer, retaining the existing OS until the
   encrypted install, work apps, meetings, VM lab, backups, and rollback path
   pass on the target hardware.

## References

- [Hexen installation guide](../install/README.md)
- [Desktop and themes guide](desktop.md)
- [Recovery procedure and VM evidence](recovery.md)
- [Application sources and update paths](app-sources.md)
- [Virtualization and network isolation](virtualization.md)
- [Omarchy update-process internals](https://github.com/omacom/omarchy/blob/quattro/docs/update-process.md)
- [Omarchy update user guide](https://github.com/omacom/omarchy/blob/quattro/manual/30-updates.md)
- [Omarchy dotfiles, hooks, and extensions](https://github.com/omacom/omarchy/blob/quattro/manual/31-dotfiles.md)
