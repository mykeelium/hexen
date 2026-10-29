# Current development checkpoint

Updated 2026-10-28. The 2026-10-26 app and recovery notes below describe the
older `hexen-archinstall` VM; they are historical evidence, not acceptance of
the clean rehearsal VM. The separate `hexen-rehearsal-20261027` VM now has
Walker 2.17.2 and all seven matching Elephant 2.22.1 providers built from the
commits in `install/manual-apps/walker/sources.lock`, reviewed, and installed.
The fixed `install/provision.sh --vm` run completed with Walker selected and
zero failed Ansible tasks. Elephant's service was started in the active user
session; Walker opened and displayed desktop applications. Direct Elephant
queries returned the expected calculator result (`1+1` -> `2`), Google search
action for a sample term, and a matching Ghostty desktop entry. Fuzzel remains
installed but is no longer the selected launcher. Repository changes are saved
but uncommitted; preserve this working copy and do not reset or clean it.

Zen Browser 1.23.4b-1 was also built from reviewed recipe commit
`ff5b152a31356577936690ccd32599e851326b85` and installed in the clean VM. Its
upstream archive passed the recipe's SHA-256 check; the local package archive
SHA-256 is `d792eb7429500d4f46a3fa0150114243cfd5cf52d6b7c43038c409f8f7682ed7`.
The VM now reports `zen.desktop` as its HTTP/HTTPS handler, and `xdg-open`
started Zen with a Google test URL. The exact Elephant activation request was
also issued; the live Hyprland client list confirmed the Google Search window
in Zen.

The clean-VM app pass installed Zoom 7.2.1-1 and Slack 4.52.182-1. Slack reached
its sign-in screen without account sign-in. Zoom opened its Workplace window,
but a later unlocked visual check found a “Zoom quit unexpectedly” report over
it. 1Password 8.12.42-36 passed its vendor signature and package checks, but
its launch opened a Crash Reporter window. A later diagnostic launch with
`--disable-gpu` reached the normal 1Password welcome window, suggesting a VM
graphics-path interaction; the VM has no accelerated virtio GPU. The normal
GPU-enabled launch still needs hardware verification. Zoom also has a recorded
SIGSEGV from its first run, though a Workplace window is running after relaunch;
its cause is unresolved. Zed logs show Vulkan adapter initialization failed
and it selected software llvmpipe despite `vulkan-virtio` being installed. The
VM's virtio video device has 3D acceleration disabled. These issues keep the
application gate open. Hyprmon at
commit `32ad27f94f40fd0dd81f982cc8208bb615607202` passed `go test ./...`, built,
and opened through the Display settings Ghostty command; its apply/save keys
have not been exercised.

Bitwarden Desktop was added to the apps role from the Bitwarden-verified
Flathub listing. In the rehearsal VM, Flatpak 1:1.18.4-2 and Bitwarden
2026.10.0 installed, the app opened to its login screen without sign-in, and a
second apps-role run reported zero changes. GNOME keyring and `libsecret` are
available. Flatpak grants broad device access plus specific browser integration
paths; its permissions were reviewed. Native messaging with Zen did not start
successfully and remains an open browser-integration check. See
[`app sources`](app-sources.md#bitwarden-flathub-follow-up-2026-10-28).

The 2026-10-28 maintenance audit accepted `pacman-contrib` in the rehearsal VM:
its weekly timer is active, the packaged `paccache -r` retains the default
three versions, and the dry run found no eligible entries. The documented
preview command was fixed to `paccache --dryrun --keep 3`. The base role now
owns `/etc/firewalld/zones/drop.xml`: target `DROP`, only `dhcpv6-client`, and
no ports, rich rules, or intra-zone forwarding. In the rehearsal VM, runtime
and permanent policy matched; `allow-host-ipv6` was active, DNS resolved, and
IPv4 HTTPS returned HTTP 200 after reload. The targeted Ansible rerun reported
`changed=0`. The VM has no IPv6 default route. Trusted-profile, LocalSend,
libvirt, VPN, and external IPv4/IPv6 acceptance remains open. See
[`operations roadmap`](operations-roadmap.md).

On 2026-10-28 the rehearsal VM advanced to the host's recorded source checkpoint
`382de1c`; its previous branch and uncommitted source diff were preserved under
`/home/mcuomo/hexen-vm-recovery/`. Lock-screen, Walker, Starship, Waybar, and
desktop-helper source files match the host checkout. Walker is the selected
launcher, managed links resolve into `/home/mcuomo/hexen`, and `hexen-theme
current` reports `gruvbox-dark`. The VM-mode full Ansible playbook completed
twice with `changed=0` and `failed=0`. PipeWire and WirePlumber are active. The
VM's `192.168.122.0/24` interface overlaps libvirt's packaged default NAT
network, so VM-mode provisioning leaves nested network management disabled;
guest DHCP/NAT and external firewall probes remain unaccepted. Normal reboot,
login/lock, application, and audio/capture checks are also still open.

Snapper cleanup passed its rehearsal check: the timer is active and the installed
7-day/10-and-5 policy matches the source. A disposable three-snapshot `number`
test pruned the oldest snapshot at a temporary two-snapshot limit, preserved all
existing recovery snapshots, and removed the test artifacts. The original policy
was restored. SSD trim remains deferred until the physical disk layout and
discard tradeoff are reviewed.

The owner created the GNOME keyring in response to the Zed prompt; its user
service is active. Account sign-in remains deferred. See the latest per-app
evidence and open checks in [`app sources`](app-sources.md#clean-rehearsal-vm-application-pass-2026-10-28).

A provisioning bug was found and fixed during this run: the VM Vulkan package
override used Ansible's free-form extra-vars syntax, which parsed the intended
list as a string. It is now passed as JSON. The provisioner's Walker package
precheck also now includes `elephant-websearch`.

## Active clean rehearsal VM

- Domain `hexen-rehearsal-20261027`, connection `qemu:///system`; this is the
  current application-acceptance VM. The owner is handling account sign-ins on
  another computer; do not enter account credentials here.
- It auto-locks during idle periods. The owner may unlock it for visual checks;
  do not type or request their passwords.
- Current package/source evidence is recorded in
  [`app-sources.md`](app-sources.md#clean-rehearsal-vm-application-pass-2026-10-28).

## Historical installed VM and access (2026-10-26)

The following VM, disk, SSH alias and commands are historical recovery notes;
they refer to `hexen-archinstall`, not the active clean rehearsal VM above.

- Domain `hexen-archinstall`, connection `qemu:///system`, currently running
  from its installed disk and already unlocked. Four CPUs, 8 GiB RAM, 64 GiB
  disposable QCOW2, UEFI with Secure Boot disabled.
- Disk `/var/lib/libvirt/images/hexen-archinstall.qcow2`.
- Persistent definition boots disk only; virtual CD-ROM is empty again.
- Hostname `hexen-vm`, user `mcuomo`, last address `192.168.122.237`.
- SSH private key remains at host `~/.ssh/hexen-vm`, without passphrase.
  Never copy or display it. Verified public host keys are in ignored
  `.local/vm/known_hosts`.
- Installed host alias `hexen-archinstall-installed`; use user `mcuomo`.
  The temporary live-ISO alias ending `recovery-20261025` is historical.
- `.local/vm/guest-exec.py` is a root-command helper through the authorized
  QEMU guest-agent channel. It takes a command after `--` or `--status PID`.
- Host libvirt/network access may require sandbox escalation. Host sudo uses
  the owner's FIDO authenticator; do not change authentication or firewall.
- The owner applied scoped UFW DHCP/DNS/forwarding rules on virbr0; DHCP,
  gateway DNS, HTTPS, and time synchronization work. See `install/vm/README.md`.

```sh
virsh --connect qemu:///system domifaddr hexen-archinstall --source agent
ssh -i "$HOME/.ssh/hexen-vm" -o IdentitiesOnly=yes \
  -o StrictHostKeyChecking=yes -o HostKeyAlias=hexen-archinstall-installed \
  -o UserKnownHostsFile="$PWD/.local/vm/known_hosts" mcuomo@CURRENT_GUEST_IP
/usr/bin/python .local/vm/guest-exec.py -- /usr/bin/systemctl --failed --no-pager
```

If the VM is shut off, start it and open its console. The owner must enter the
LUKS passphrase interactively; never retrieve or log it.

```sh
virsh --connect qemu:///system start hexen-archinstall
/usr/bin/python /usr/bin/virt-manager --connect qemu:///system \
  --show-domain-console hexen-archinstall
```

## Verified installation and recovery

Archinstall 4.5 installed LUKS2 directly containing Btrfs. Separate siblings
are `@`, `@home`, `@log`, and `@pkg`; ESP is FAT at `/boot`. Limine 12.9.4 owns
`/boot/EFI/arch-limine/` and the installer's `99-limine.hook`. Mapper is `root`,
root subvolume `@`, non-UKI entry, mkinitcpio `encrypt` hook. Kernel remains
`7.2.11-arch1-1`. NetworkManager, SSH, and guest agent are active; zram is the
only swap. There are no failed services. ISO credential exports were deleted.

The boot role is read-only and runs before provisioning. It audits root/ESP,
LUKS ancestry, saved/running parameters, a complete single Limine entry, ordered
initramfs hooks, kernel preset/drop-ins, package hook, and the deployed EFI
binary. Independent review findings were fixed with regression tests, including
duplicate parameters, split entries, overridden hooks, no-op update action,
false-positive rejection tests, and symlinked drop-in directories.

Recovery passed on 2026-10-26 using the original live ISO and owner-entered
passphrase. Snapshot 1 restored to writable `@` (ID 264). Previous root remains
`@failed-recovery-test` (ID 256); do not delete it. Root probe reverted to
`before-recovery-test`; home probe remained intact. Sibling IDs 257/258/259 and
nested portables/machines/Snapper IDs 260/261/262 were preserved. Matching ESP
archive restored; kernel/initramfs/EFI checksums and package manifest matched.
Snapper listed snapshot 1 and created snapshot 2 after the successful restored
boot. See `docs/recovery.md` for commands, scope, and evidence.

`pacman -Syu` found no newer packages. On 2026-10-28, Arch's official
[`linux` package page](https://archlinux.org/packages/core/x86_64/linux/)
listed `7.2.11.arch1-1`, the same kernel version installed in the VM.
Reinstalling current official `linux` and
`limine` exercised the actual initramfs rebuild and EFI copy hooks, followed by
a successful reboot. Optional `qat_6xxx` firmware warning was recorded. An
actual transition to a newer kernel remains untested.

Root-owned test records and backup are on encrypted home at
`/home/mcuomo/hexen-vm-recovery/`, including `snapshot-number`,
`boot-before-update.tar`, checksums, package manifests, subvolume lists,
transaction logs, and test logs. No secret was copied to the repository.
The saved original disk-only definition is also in
`.local/vm/disk-boot-before-recovery.xml` and has already been restored.

## VPN and virtualization packages added

The base package list now includes Arch's `openvpn`; the desktop list adds
`networkmanager-openvpn` and `nm-connection-editor`, plus `qemu-desktop`,
`libvirt`, `virt-manager`, `virt-install`, `virt-viewer`, `edk2-ovmf`,
`dnsmasq`, and `swtpm`.
The desktop role enables the modular QEMU, network, and storage libvirt sockets,
preserves or defines the packaged `default` network, and starts/autostarts it.
It also configures the `default` directory storage pool under
`/var/lib/libvirt/images`, refusing to replace a custom existing pool.
It does not add the user to the broad `libvirt` group; desktop Polkit handles
system-management authorization. OpenVPN profiles and Windows VM images stay
outside the repository. See `docs/virtualization.md` for isolation and use notes.

The current host uses virt-manager with `qemu:///system`, an active/autostart
default NAT network, and the same core libvirt/QEMU packages. The repo chooses
the Arch `qemu-desktop` split package for x86 guests rather than installing all
QEMU emulators. These latest package and service changes have not yet been
provisioned or verified in the disposable Arch VM. No GOAD/Vagrant project files
were found in this repository or common home/source locations, so the local
provider-specific lab automation has not been imported.

## Application state

The automatic apps role installs signed official Neovim 0.12.6-1, Lazygit
0.66.2-1, and Obsidian 1.14.5-1. The owner editor configuration/plugins/tools
are now merged, installed and tested. Obsidian's first window was verified;
no vault or account was created. Desktop/editor evidence follows below.

All four reviewed non-repository apps are now installed through the one-off
manual validation sequence: 1password 8.12.42-36, zen-browser-bin 1.23.4b-1,
zoom 7.2.1-1, slack-desktop 4.52.182-1. The vendor public key was imported only
into the VM build user's GPG keyring for source verification. No pacman trust
policy/repository key, AUR helper, Flatpak remote, or unattended build role was
added. Source/privilege/integrity evidence and pending first-launch details are
in the later third-party installation section and `install/manual-apps/`.

## Earlier base/official-app verification

- Post-recovery boot tests, normal/check: `ok=46 changed=0 failed=0 rescued=2`.
- All 19 configuration cases: `ok=139 changed=0 failed=0 rescued=18`.
- Post-recovery provisioning before apps: `ok=41 changed=0 failed=0`.
- With apps: first run `ok=42 changed=1 failed=0`; second run
  `ok=42 changed=0 failed=0`. Full syntax check passed.
- SSH used the previously verified installed host key; HTTPS 200, synchronized
  time, active services, and zram-only swap verified. No failed services after apps.
- Root, home, boot-file, package, and Snapper assertions passed. Test audits
  preserve boot artifacts. Tests with `rescued` counts intentionally reject
  invalid fixtures; those are not unexpected failures.
- Host `git diff --check` passed. No commits made.

VM source copy is `/home/mcuomo/hexen`. Recopy local `ansible/` and `tests/`
changes before subsequent VM tests. Use `ANSIBLE_CONFIG=ansible/ansible.cfg`
for full provisioning and `ANSIBLE_ROLES_PATH=ansible/roles` for tests.

## Desktop and editor implemented on 2026-10-26

The owner supplied `~/.config/nvim` and `mykeelium/nvim-config`, then explicitly
selected GitHub `base` plus the inclusive union of `numen` and `arcana`, and
requested close Omarchy default bindings. No pending preference questions remain.
The local host config is Omarchy/LazyVim and was not imported or modified.

Source clone `/tmp/hexen-owner-nvim`, commit
`e45b8249bfb152c20f9089100ca95f00eeef5ba1`, has several profiles and 629 MiB of
cached nvim-data. Only Base source/lockfiles plus Numen's added leader-li mapping
were imported into `config/nvim`; no caches/binaries or backup files. Base's
active features are a superset of Arcana, so no features were removed. Python
provider path was made portable; lazy bootstrap uses the lockfile pin. Mason v2
compatibility and native Treesitter setup were fixed after real regression
failures. All 13 parsers and 5 language tools installed through explicit
user-local `setup.lua`; normal startup no longer races automatic Mason installs.
34 plugin sources/commits and observed language-tool receipt versions are in
`config/nvim/PLUGIN-SOURCES.md` and README. A pinned plugin's harmless
vim.tbl_flatten deprecation warning remains; project-level LSP/DAP tests pending.
Go's Delve debugger is installed from official Arch packages; OmniSharp --help
and gopls version checks passed.

The new opt-in desktop role is enabled by `-e desktop_user=mcuomo` in this VM;
omitting the variable retains the previous boot/base/apps path. It links
`config/{hypr,waybar,ghostty,mako,fuzzel,xdg-desktop-portal,nvim}` and the
`hexen-desktop` helper. It rejects root, foreign/unmanaged target configs and
symlinked/foreign-owned .config/.local/.local/bin parents. It preserves existing
parent permissions and only creates absent parents, and link metadata changes
do not follow into source targets. Tests reproduced both metadata/symlink
findings before fixes. Root/private-dir/symlink fixtures were cleaned up.

Current Hyprland 0.56 requires Lua config, so the shared files are
`config/hypr/hyprland.lua`, `theme.lua`, and editable `bindings.lua` rather than
the old plan's config syntax. There are 121 registered bindings following the
local Omarchy revision `8e03151647ef210ce9e313180e642d3e58dbe9a6`. License retained.
Walker/Elephant were not in official repos; Fuzzel is the documented first-pass
launcher on the same key. The later manual application stage installed four
AUR-built packages and a source-verification public key in the build user's
GPG keyring; those are not installed by the desktop role.
The launcher setup now defaults to Walker and offers official Fuzzel as an
install-time option. Walker requires the owner to manually build and install
the reviewed, pinned Walker/Elephant packages. Provisioning verifies Walker's package and
provider prerequisites but does not build AUR recipes. Both launcher choices
share the Hexen dispatcher for Super+Space, Super+Escape, menus, Waybar pickers,
and clipboard selection. Walker's selected integrations are desktop apps,
files, runner, calculator, and provider navigation; package search, AUR,
Bluetooth, and clipboard providers remain disabled. See `docs/desktop.md` and
`install/manual-apps/walker/README.md`. This is source/pin review and repeatable
recipe guidance, not a bit-for-bit reproducible binary build guarantee.
See `docs/desktop.md` for startup, parity, omissions, package/runtime inventory,
clipboard storage, lock policy, and tests. Host Omarchy source/config was read-only.

Desktop package install initially failed before committing any packages because
Fastly lacked a python-dbus signature. A full `pacman -Syu` resolved stale mirror
metadata without disabling signatures; upgraded btrfs-progs, libsoup3, llvm-libs
but kernel version remained unchanged. Fresh checkpoint is snapshot 3,
`hexen-before-desktop-retry`, with `boot-before-desktop.tar` in the VM record
folder. Desktop dependencies and language runtimes were then installed from
official packages. Final package/dependency records are in that folder.

## Current graphical session and verification

A transient `hexen-desktop-test2.service` creates a normal-user PAM/login/UWSM
session on VM tty7. It is running. The owner unlocked its idle lock for further GUI tests; it may
automatically lock again after five idle minutes. Unlock using the VM account
password, not the LUKS passphrase. No persistent autologin, account-password change, or display
manager was configured. Normal startup is a local login then
`uwsm start hyprland.desktop`. This test service vanishes on reboot.

The first harness session enumerated input before activating its VT. Restarting
with tty7 active first resolved it; no input-group membership or relaxed device
permissions were used. Both keyboard and pointer now enumerate. Actual
Super+2, Super+Enter, and Super+Space tests passed, as did a synthetic clipboard
round trip. The clipboard owner test process was cleaned up. Waybar, Mako,
Hypridle, PipeWire, WirePlumber and both portal services run, with no failed user
units. Configuration reload reports no errors. Idle lock renders. VM screenshot artifacts are ignored under `.local/vm/`. The earlier
`desktop-editor.png` captured a lock screen. After the owner unlocked the
account, `editor-unlocked.png` verifies the actual merged Neovim UI and
`obsidian-unlocked.png` verifies Obsidian's initial setup window.

Final checks after fixes:

- Full opt-in provision after adding Delve: `ok=59 changed=1 failed=0`; second
  run `ok=59 changed=0 failed=0`. Syntax passed.
- Desktop protection test: `ok=40 changed=5 failed=0 rescued=3`; changes are
  test fixture setup/cleanup. Metadata guard test: `ok=50 changed=10 failed=0
  rescued=1`, with original .config mode restored and isolated account removed.
- Boot integration `ok=46 changed=0 failed=0 rescued=2`; all 19 malformed/valid
  config cases `ok=139 changed=0 failed=0 rescued=18`.
- Final owner-editor test passed after normal lazy-load scheduling: preserved
  debugger/Oil/Snacks/Telescope, Numen LSP mapping activation, custom Lua settings,
  all parser loads, all five tool executables, portable Python provider and Delve.
- Three Python menu-safety tests passed (cancel, arbitrary typed shell text,
  explicit lock selection); shell syntax check and git diff --check passed.
- Independent review of role/editor/docs finished with no additional material
  findings after parent-directory safeguards were fixed.

## Additional acceptance after owner unlock

- Actual Super+Shift+N opened the merged editor; its visible theme/bufferline/UI
  rendered correctly. Super+F entered fullscreen and returned to tiling.
- Actual Super+Shift+O opened Obsidian's initial vault-selection window. No vault
  was created and no account was signed in.
- New `tests/editor-project.lua` passed using a temporary dependency-free Go
  module: gopls attached and returned variable hover, and nvim-dap-go/Delve
  launched and stopped on entry. The module was removed and debugger terminated;
  a subsequent process check confirmed no `dlv` remained.
- Live compositor reports no config errors; no failed system or user units.
- No production source changed during these checks. Documentation/checkpoint and
  the new project-level smoke test were saved; all changes remain uncommitted.

## Third-party application installation and first launch

The owner requested continued implementation. Ruling: manual builds means
one-off reviewed commands performed by the agent under the owner's VM install
authorization, not AUR automation in Ansible or unattended trust prompts.

Snapshot **4**, `hexen-before-third-party-apps`, precedes installation. Recipe
remote heads still matched all four reviewed commits. Exact clean tracked trees
were copied into `/home/mcuomo/hexen-vm-builds/{1password,zen-browser-bin,zoom,slack-desktop}`.
All declared source hashes passed. 1Password's vendor key was fetched directly,
primary fingerprint matched the official documentation, imported into only the
normal build user's GPG keyring, and detached source signature verification
passed. Pacman trust/signature settings were unchanged.

Missing signed dependencies installed with --asdeps: mailcap (mime-types
provider), dbus-glib, ttf-dejavu (ttf-font provider), libxss. All four packages
built as mcuomo without sudo/root or --syncdeps. 1Password emitted a fakeroot
warning during tidying but completed; all archive paths/uid/gid and privileged
modes were inspected, as were installed metadata afterward. The only install
script exactly matched reviewed 1password.install. All archive entries had
root owners. No new service/autostart units found. Root rechecked the package
SHA-256 values immediately before one pacman -U transaction.

Installed versions: 1password 8.12.42-36, zen-browser-bin 1.23.4b-1,
zoom 7.2.1-1, slack-desktop 4.52.182-1. `pacman -Qkk` found no altered files for
Zen, Zoom, Slack. 1Password's only altered file is the intentional BrowserSupport
GID/mode change by its install script: root:onepassword 2755. Its sandbox and
Slack's sandbox are root:root 4755. Generated Polkit owners contain only mcuomo;
the desktop user is NOT in onepassword. No user/system units failed.
Main provisioning after installation: `ok=59 changed=0 failed=0`.

Recipes, downloads, verify/build logs, archives and `verified-packages.json`
remain in the build directory. Public copy of the inspection manifest is
`install/manual-apps/validation-2026-10-26.json`; `.local/vm/third-party-packages.json`
is also retained. Installed manifests/diff, integrity and transaction logs are
in `/home/mcuomo/hexen-vm-recovery/`. Built hashes are per-run audit records,
not promises that later/machine-specific builds produce the same bytes.

After the owner created the GNOME “Default Keyring” in the VM, Slack opened to
its normal sign-in screen. Zen and 1Password reached their welcome screens and
Zoom opened to Zoom Workplace. Zen is the default for HTTP and HTTPS. The
keyring service is running; no account was signed in and no vault or meeting was
created. The owner prefers to handle account sign-ins on another computer.
No 1Password browser trust allowlist or extension setup has been performed.

## Host launcher preview, 2026-10-27

The active host uses Omarchy with Hyprland 0.55.2; the full Hexen Hyprland
configuration requires 0.56+, so it was not applied. A small legacy syntax
overlay in `config/hypr/launcher-preview-compat.conf` routes Super+Space to the
Hexen Walker app launcher and Super+Escape to its system/power picker while
leaving the rest of the current desktop intact. `~/.config/walker` points to
the repo config, the Hexen launcher setting is `walker`, and the Elephant user
service is active. Hyprland reload and `hyprctl configerrors` completed cleanly.
The original Walker config and bindings file were preserved at
`~/.config/walker.omarchy-backup-20261027-132746` and
`~/.config/hypr/bindings.conf.hexen-backup-20261027-132746`.

The existing Walker/Elephant packages are 2.16.2/2.21.0 from the configured
Omarchy repository (`SigLevel = Optional TrustAll`), not the reviewed pinned
builds described in the Walker manual guide. No Walker packages were installed
or upgraded in this preview. An attempted Fuzzel install failed because the
Omarchy stable mirror returned 404 for official Arch packages; pacman committed
no package transaction. Fuzzel is unrelated to previewing these two Walker
windows. Use the manual pinned Walker build guide for a trusted Hexen install.

## Next work

1. Test native browser/password shortcuts and, if desired, configure the
   documented Zen/1Password browser integration. Accounts can be signed in on
   another computer; this is separate from provisioning.
2. Test Zoom screen sharing through the Wayland portal. Active portals or a
   mapped Zoom window do not prove a successful share.
3. Finish remaining desktop interactions, other language/project workflows,
   and theme choices. Basic editor GUI and Go LSP/DAP are verified.
4. Test a real newer-kernel upgrade/reboot when available; kernel unchanged.
5. Finish hardware/readiness checks before wiping the laptop; not ready yet.

Ruling: continue in this existing dirty workspace to preserve saved work and the
VM source copy. Do not reset, clean, or migrate the branch as a workflow step.
