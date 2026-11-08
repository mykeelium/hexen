# Work XPS 14: wiped disk to accepted workstation

Updated 2026-11-06. Target: Dell XPS 14 9440, Intel `8086:7d55` and NVIDIA
`10de:28a1`, using the three-screen Tessmart DisplayPort MST KVM.

This is the owner's chosen internal-install path: install onto the wiped drive,
then accept the actual hardware and work applications. A separate external-disk
trial is not a prerequisite for this path. Installation success alone does not
establish work readiness. Reserve time to troubleshoot or restore the previous
OS if essential hardware or work functions fail.

**VPN configuration and testing happen only on the work XPS after installation.**
Do not import the work profile or test corporate access on a personal computer
or rehearsal VM.

## 0. Starting conditions and reference revision

This guide starts after deliberate disk preparation. It contains no wipe command.

- [ ] The internal drive has been identified and prepared as a blank whole disk.
- [ ] Independent backups, required credentials and recovery media are available
  outside the laptop. Backup storage is disconnected during installation.
- [ ] The saved OpenVPN profile and any referenced certificates, private keys
  or authentication files are available through an employer-approved transfer.
- [ ] Employer requirements are understood. Drata remains an unresolved separate
  gate; installing the OS does not resolve its Arch support issue.
- [ ] The laptop is connected to AC power. Another computer is available to
  read these instructions or download recovery material.
- [ ] Verified x86_64 Arch installation media is available. The wrapper supports
  **Archinstall 4.5 exactly**; the recorded rehearsal ISO is 2026.10.01. Do not
  assume the newest ISO has the required installer version.
- [ ] Firmware boots UEFI, with Secure Boot disabled. Leave both GPUs enabled.

The reviewed software candidate for these instructions is:

```text
8f6d3808f10616e71ba0bc949c19451405ff08c1
```

It passed 96 local tests with no skips, the three GitHub CI jobs and anonymous
archive verification on the earlier verification run. This is software evidence,
not an accepted physical-laptop release. Do not silently substitute current
`main`. If a later candidate is selected, record its full revision and repeat
the affected checks. Use one identical revision for the live and installed stages.

The XPS hardware inventory has already passed: correct model and both GPU IDs,
UEFI and disabled Secure Boot. Rerun it on the live ISO below.

## 1. Boot the Arch live environment

Boot the verified USB in UEFI mode. Start with the laptop panel available so a
KVM/display problem does not hide the installer. The ISO shell runs as root.
Enter Bash because the command blocks below use Bash syntax:

```bash
bash
```

Confirm UEFI and the supported Archinstall version:

```bash
test -d /sys/firmware/efi && echo 'UEFI boot confirmed'
python3 -c 'import importlib.metadata; print(importlib.metadata.version("archinstall"))'
```

Expected: UEFI confirmed and `4.5`. If either differs, stop and use compatible
media; do not edit the version check to bypass it.

Connect ordinary internet access, without the work VPN. Wired networking may
connect automatically. For Wi-Fi, enter `iwctl`, run `device list`, then use the
actual device name with `station DEVICE scan`, `station DEVICE get-networks`,
and `station DEVICE connect SSID`. Enter the password interactively, then `exit`.

```bash
ip address
curl -I https://archlinux.org
timedatectl status
```

Expected: an address, working HTTPS and a reasonable clock. If necessary enable
time synchronization with `timedatectl set-ntp true` and wait for synchronization.
Do not start installation while networking or the clock is broken.

## 2. Check the prepared disk without modifying it

```bash
lsblk -o NAME,PATH,TYPE,SIZE,MODEL,SERIAL,TRAN,FSTYPE,PTTYPE,MOUNTPOINTS
```

Identify the internal disk by model, serial and capacity. The wrapper requires
a writable whole disk of at least 40 GiB with no child partitions, partition
table, filesystem signature or mountpoint. Do not select the installation USB.
Do not copy `/dev/vda` from VM instructions.

If the old layout is still visible, stop: disk preparation is not complete.
This guide assumes that step is finished and does not erase a detected disk.
You can inspect a specifically identified device's signatures with
`wipefs --no-act /dev/ACTUAL_WHOLE_DISK`; `--no-act` is inspection only.

## 3. Download the candidate and preview the plan

In the live Bash shell:

```bash
HEXEN_REVISION=8f6d3808f10616e71ba0bc949c19451405ff08c1
cd /root
curl -fL --retry 3 -o /tmp/hexen-source.tar.gz \
  "https://github.com/mykeelium/hexen/archive/$HEXEN_REVISION.tar.gz"
```

Continue only if the download succeeded. Then:

```bash
bsdtar -xf /tmp/hexen-source.tar.gz
cd "/root/hexen-$HEXEN_REVISION"
python3 install/hardware.py --profile xps-14-9440
```

Expect the same model/GPU report previously obtained and `secure_boot: false`.
This is a read-only inventory, not a package installation.

Preview the installer:

```bash
./install/archinstall/hexen-install.sh --hardware xps-14-9440
```

Choose the actual internal disk and enter hostname, regular username, timezone
and other requested values. Use the supported US keyboard layout. Review:

- Correct disk model, serial and size.
- LUKS2 encryption and encrypted Btrfs root.
- Separate root/home/log/package-cache subvolumes and FAT ESP at `/boot`.
- Limine bootloader, UKI disabled and the standard `linux` kernel.
- XPS graphics packages: `mesa`, `vulkan-intel`, `intel-media-driver`,
  `nvidia-open`, `nvidia-utils`, `nvidia-prime`, plus `linux`.
- Networking and your regular account.

The preview is a separate run; the installation run may ask for selections again.
If anything is wrong, correct the cause before proceeding.

## 4. Install the base system

From the same source directory:

```bash
./install/archinstall/hexen-install.sh --hardware xps-14-9440 --install
```

Review selections again. At the destructive confirmation, enter the exact disk
path requested by the wrapper. Choose an encryption passphrase and account
password; retain them outside the laptop. They serve different purposes.
Hidden password input showing no characters is normal.

Review the loaded Archinstall plan before choosing Install. Preserve the
generated boot/encryption/layout choices; do not change them to bypass a check.
Do not select Save credentials or share generated credential files.

Wait for successful completion. Package downloads and initramfs generation can
take time. If installation fails after making disk changes, stop and inspect
the error. The wrapper does not resume or automatically clean a partial install;
do not repeatedly restart it or disable package signature checking.

After success, exit the installer, run `reboot`, and boot the internal drive
instead of the USB. Keep recovery media available.

## 5. First installed boot: encrypted console login

At Limine, boot the installed entry. Enter the LUKS passphrase, then log into
the console as the regular account created during installation. A console login
is expected: the graphical desktop is provisioned in the next stage.

Use `nmtui` to activate Wi-Fi if needed. Confirm ordinary internet access:

```bash
curl -I https://archlinux.org
lsblk -f
findmnt /
findmnt /home
findmnt /boot
swapon --show
```

Expect encrypted Btrfs root on subvolume `@`, a separate home subvolume, FAT ESP
at `/boot`, and no disk-backed swap. Zram is allowed. Inspect the actual LUKS
partition identified by `lsblk`:

```bash
sudo cryptsetup luksDump /dev/ACTUAL_LUKS_PARTITION
```

Expected header version: `2`. If encryption or the layout is wrong, stop before
restoring work files. See [boot verification](../install/archinstall/README.md#verify-after-first-boot).

## 6. Obtain the permanent checkout

Run these as your regular installed user, in Bash, not as root. The source on
the live ISO does not survive as your installed checkout.

```bash
bash
HEXEN_REVISION=8f6d3808f10616e71ba0bc949c19451405ff08c1
git clone --no-checkout --branch main https://github.com/mykeelium/hexen.git "$HOME/hexen" &&
  cd "$HOME/hexen" &&
  git merge-base --is-ancestor "$HEXEN_REVISION" origin/main &&
  git switch --create hexen "$HEXEN_REVISION" &&
  git branch --set-upstream-to=origin/main hexen &&
  test "$(git rev-parse HEAD)" = "$HEXEN_REVISION"
```

Continue only if the entire chain succeeded. Confirm:

```bash
git rev-parse HEAD
git status --short
git branch -vv
```

Expected: the full candidate commit, no working-tree changes and branch `hexen`
tracking `origin/main`. If the destination already exists, inspect it rather than
deleting/resetting it. Keep this checkout at `~/hexen`: managed configuration
links depend on its location.

## 7. Provision the XPS desktop

```bash
cd "$HOME/hexen"
./install/first-boot.sh --hardware xps-14-9440
```

Do **not** add `--vm`, and do not run the wrapper through `sudo`. It requests
privilege when required. The Ansible BECOME password is your account password.

The wrapper performs a reviewed full Arch update, installs the matched XPS
graphics stack and provisions the system. If a kernel/package mismatch is
reported, follow the full-update guidance; do not install an old driver or
perform a partial upgrade to bypass it.

Choose a launcher:

- **Fuzzel:** official Arch package, fewer build steps.
- **Walker:** guided pinned Walker/Elephant/provider builds. Read each recipe,
  source-verification result and package review before approving. In the pager,
  `q` exits. Do not mix unmatched provider builds or substitute arbitrary versions.

Both are supported selections. See [Walker instructions](../install/manual-apps/walker/README.md).
Allow time for source builds. Read all failed-task output; a partial provisioning
run is not completion. Correct the cause and follow the printed retry guidance
using the same first-boot command. A retry may run a full Arch upgrade again.

After successful setup:

```bash
python3 install/health.py
```

Follow the health report's reboot instruction. Do not try to rebind GPUs live.

## 8. First graphical login and GPU checks

Reboot, unlock LUKS, and sign into SDDM using your regular account. Select
**Hyprland (UWSM-managed)** in the session selector.

Open Ghostty with Super+Enter. From the checkout:

```bash
cd "$HOME/hexen"
python3 install/hardware.py --profile xps-14-9440 --runtime
nvidia-smi --query-gpu=name,driver_version --format=csv,noheader
hyprctl monitors -j
hyprctl configerrors
systemctl --failed
systemctl --user --failed
python3 install/health.py
```

Expected: runtime verification succeeds; NVIDIA is detected; monitor inventory
is plausible; no Hyprland configuration errors or unexplained failed services.
The hardware checker verifies DRM aliases/modesetting, not visual correctness.

Do not force `xe`, disable either GPU or add unreviewed NVIDIA environment
variables in response to a failure. Capture the exact error and investigate.

If graphical login fails, use a text console such as Ctrl+Alt+F3 (possibly with
the laptop Fn key), log in normally and inspect:

```bash
systemctl status sddm --no-pager
journalctl -b -u sddm --no-pager
systemctl --failed
```

Try the laptop panel with the KVM disconnected to distinguish external-output
failure from a session failure. Use the [desktop guide](desktop.md) for recovery;
do not erase/reinstall merely because SDDM or one display fails.

## 9. Accept displays, KVM and power behavior

Connect the XPS to the KVM. The personal XPS 15 and other Arch machine working
with it are useful context; they do not establish this XPS 14's GPU/MST behavior.

- [ ] Three independent 1920x1200 external displays work at the expected roughly
  60 Hz refresh, with correct physical ordering.
- [ ] The middle display has the intended initial focus/workspace behavior.
  Hyprland does not use XRandR's primary-display setting in the same way.
- [ ] The laptop panel is enabled/disabled as desired without losing all outputs.
- [ ] Keyboard, mouse and any KVM-connected audio/USB devices work.
- [ ] Switch away and back several times; windows and inputs recover.
- [ ] Disconnect/reconnect USB-C; outputs recover.
- [ ] Test lid behavior docked and undocked. Save work first.
- [ ] Lock/unlock docked and undocked; confirm authentication is required.
- [ ] Suspend/resume docked and undocked; confirm display, input, audio and
  networking return. Test from the system menu while physically present.
- [ ] Check brightness, battery reporting, AC transitions and reasonable thermals.

Use actual names from `hyprctl monitors -j`, not Mint/XRandR connector names.
For persistent arrangements use the existing machine-local monitor workflow or
`~/.config/hypr/local.lua`. Super+K opens local overrides. Display settings opens
Hyprmon when installed, otherwise its installation guide. See
[display settings](desktop.md#display-settings-and-walker-searches).

After an arrangement change, run `hyprctl configerrors`, test re-login/reboot,
and confirm `git -C "$HOME/hexen" status --short` remains empty. Keep machine
configuration outside tracked defaults.

## 10. Desktop and peripheral smoke test

- [ ] Super+Space opens the selected launcher and finds Firefox.
- [ ] Super+Shift+B opens the browser; Super+Shift+Alt+B opens a private window.
- [ ] If using Walker, `=2+2` produces 4 and an explicit `@test phrase` search
  opens only when selected and activated.
- [ ] Super+Alt+Space opens the Hexen menu. Open Getting started, Network,
  Audio, Bluetooth, Diagnostics and Review updates. Opening review is not
  permission to install updates; cancel when only checking the interface.
- [ ] Diagnostics and Review updates work from the menu, not just an interactive
  terminal. Earlier candidates had a graphical command-lookup failure.
- [ ] Idle lock, manual lock, notifications and clipboard/screenshot shortcuts work.
- [ ] Wi-Fi, Bluetooth, speakers, headphones, microphone and camera work.

Check audio services if necessary:

```bash
systemctl --user is-active pipewire wireplumber
wpctl status
```

Use Pavucontrol and the application's device selector to choose actual devices.
Do not assume a running audio service proves usable microphone or speaker audio.

## 11. Restore the work VPN on this laptop only

Do this after the graphical desktop and ordinary internet access work.
Transfer the saved profile and all required companion files to private storage
on the encrypted work laptop, outside `~/hexen`. For example, create a destination:

```bash
install -d -m 0700 "$HOME/.local/share/work-vpn"
```

Copy files there using your approved transfer method. Restrict each private
profile/key file to your user, for example `chmod 600 /actual/private/file`.
Keep referenced certificate/key paths valid; do not delete companion files after
import unless you have verified NetworkManager no longer depends on them.

Confirm the expected packages exist:

```bash
pacman -Q openvpn networkmanager-openvpn nm-connection-editor
```

They are part of Hexen's declared package selection. If absent, inspect the
provisioning result instead of treating it as successfully completed.

### Import and connect

Either open `nm-connection-editor`, add/import a saved VPN connection and select
the `.ovpn` file, or use the terminal:

```bash
nmcli connection import type openvpn file "$HOME/.local/share/work-vpn/ACTUAL_PROFILE.ovpn"
nmcli -f NAME,UUID,TYPE connection show
```

Record the imported VPN connection's UUID privately. Substitute it below:

```bash
nmcli --ask connection up uuid ACTUAL_VPN_UUID
nmcli connection show --active
```

`--ask` requests missing credentials interactively. Use the employer's MFA and
Linux profile instructions. Do not place passwords, tokens or private keys in
commands, shell history, Git or shared logs. Avoid `nmcli --show-secrets`.

The import supports common OpenVPN profiles. External authentication scripts,
browser SSO, separate credential files or unsupported directives may need
administrator guidance; do not remove security directives to force connection.

### Verify actual work access

```bash
ip route
ip -6 route
nmcli device show
```

Keep these outputs private; they can reveal internal network information.
Use a real employer-provided hostname to check internal DNS:

```bash
getent hosts ACTUAL_INTERNAL_HOSTNAME
```

- [ ] VPN connects and completes required MFA.
- [ ] Internal DNS resolves the intended resources.
- [ ] Required internal websites/services work, using approved authentication.
- [ ] Work Git access works, using the required SSH/HTTPS method.
- [ ] Routing matches employer expectations for split versus full tunnel.
- [ ] Ordinary internet access behaves as expected while connected.
- [ ] Disconnect, reconnect and test after suspend/resume. Confirm that a lost
  tunnel behaves according to employer policy; no kill switch is assumed.

Disconnect deliberately when appropriate:

```bash
nmcli connection down uuid ACTUAL_VPN_UUID
```

If connection fails, inspect local NetworkManager logs and the supplied profile
with your administrator. Do not disable firewalld or certificate verification
as a workaround. See [VPN notes](virtualization.md) and the
[NetworkManager reference](https://networkmanager.dev/docs/api/latest/nmcli.html).

## 12. Restore accounts, work files and applications

Restore work data through the approved method. Verify representative files
against the backup. Restore application data selectively rather than copying an
entire old desktop configuration over the managed Hexen configuration.

Set up Firefox, the required password manager, SSO and work Git credentials
yourself. Verify vault/account recovery before relying on local cached sessions.
Do not commit secrets, corporate project content or VPN files to the Hexen repo.

Firefox is included. Zoom and Slack are **separate reviewed manual installs**;
first boot does not silently install them. Their recorded recipe/package versions
are historical evidence, not instructions to install obsolete binaries.

For each required application:

1. Read the [application inventory](app-sources.md) and
   [manual installation procedure](../install/manual-apps/README.md).
2. Recheck current vendor instructions and review the selected AUR recipe,
   its source URLs, checksums/signatures, dependencies and referenced scripts.
3. Record the recipe revision. Review text before executing `makepkg`, including
   `makepkg --verifysource`, which itself sources the recipe.
4. Build as a normal user on a fully updated system. Review any additional AUR
   dependency with the same process; never build as root or skip verification.
5. Inspect the actual built archive's metadata, file ownership, special modes,
   install scripts, service/autostart entries and hash.
6. Install only that exact reviewed archive with `sudo pacman -U`, then launch
   the application as the desktop user and complete account sign-in.

The source inventory names `zoom` and `slack-desktop` as the reviewed packaging
paths. Do not add an arbitrary repository or AUR helper just to bypass review.
See [the command template](app-sources.md#manual-installation-procedure-after-review).

### Work meeting acceptance

- [ ] Slack workspace/SSO works and notifications arrive while another app is focused.
- [ ] Join a Zoom test meeting; another participant confirms microphone and camera.
- [ ] Confirm speaker/headset output and microphone switching.
- [ ] Share each required display through the Wayland portal; the other participant
  confirms actual content and readability.
- [ ] Check any required window-only sharing against the installed Zoom client's
  current Wayland support. Do not assume it works because display sharing works;
  if essential and unavailable, keep work acceptance open.
- [ ] Stop sharing, leave/rejoin, and repeat a short test after suspend/resume.

The earlier VM had Zoom crash reports. A welcome window is insufficient evidence;
the actual work-XPS meeting test is required. Do not disable application sandboxes
to conceal a startup failure.

## 13. Accept the development workflow

```bash
git --version
go version
command -v gopls
command -v dlv
```

Clone an approved representative project onto the work laptop, connect the VPN
where required, and follow its actual onboarding/build instructions.

- [ ] Git authentication and private dependency access work.
- [ ] The project's required Go version is available; compare with `go.mod` and
  project guidance rather than assuming the system version is suitable.
- [ ] Build and tests pass. For a project that uses these commands, run
  `go build ./...` and `go test ./...` from that project's directory.
- [ ] Editor language server, formatting, test execution and debugging work.
- [ ] Required containers, local databases or VMs work if the job needs them.
- [ ] VPN routing does not conflict with local container/libvirt networks.
- [ ] A representative edit/build/test/debug cycle completes successfully.

Do not copy personal-device corporate credentials or generate substitute access
tokens outside the employer's approved process.

## 14. Verify repeat provisioning and record a baseline

Before making changes, inspect the command's help if its behavior is unfamiliar.
From the regular user's terminal:

```bash
cd "$HOME/hexen"
git status --short
hexen config status
hexen config diff
hexen config apply
```

The saved XPS hardware selection is reused. Do not pass `--vm`. Review changes
before applying. Expect a repeat run to be unchanged, apart from understood
machine-state changes. Explain unexpected changes or failures before acceptance.
Confirm local monitor layout and theme choice survive and rerun the GPU/desktop
checks after any requested reboot.

Record baseline evidence locally in private storage:

```bash
install -d -m 0700 "$HOME/.local/state/hexen/work-acceptance"
cd "$HOME/hexen"
git rev-parse HEAD
uname -r
pacman -Q linux limine nvidia-open nvidia-utils hyprland
systemctl --failed
systemctl --user --failed
```

Record date, actual source revision, kernel/driver versions, display arrangement,
VPN/meeting/project outcomes and unresolved issues. Review logs before sharing;
omit corporate hostnames, keys, credentials and private source.

## 15. Establish update and recovery readiness

Read [maintenance](maintenance.md), [updates](machine-profiles.md#checking-update-status)
and [offline recovery](recovery.md) before the first maintenance transaction.
Root snapshots and EFI archives are a pair; neither substitutes for independent
home/work-data backups. Do not use `snapper rollback` as a shortcut for the
documented explicit `subvol=@` restore procedure.

First inspect updates:

```bash
hexen update --check
```

When ready for an actual maintenance window, save work, keep AC and reliable
networking, and run:

```bash
hexen update
```

Review each source/package/migration/configuration prompt. Source updates may
offer a different revision: inspect it and record the resulting commit rather
than assuming it is still the installation candidate. Keep the checkout clean
and do not run concurrent Pacman operations.

Confirm the workflow creates the root snapshot, matching EFI archive/checksums
and package manifests. Record the actual checkpoint path printed by the command.
After successful updates, reboot when appropriate, then repeat GPU, encrypted
boot, KVM, VPN and meeting checks. Record installed/running kernel versions. If
no newer kernel was offered, the newer-kernel transition remains untested.

The full offline restore should be rehearsed on a disposable VM using this
layout/candidate before depending on it. Do not deliberately roll back live work
data just to tick a checkbox. Physical recovery readiness includes access to the
USB media, LUKS passphrase, backup and matching recovery pair.

If the installed system cannot boot: use the Arch USB, identify the actual disk,
unlock it and follow [offline recovery](recovery.md#offline-recovery-from-arch-installation-media).
Use its ordered steps and actual snapshot/archive paths; do not invent a root
replacement or restore an unrelated ESP archive.

Manually built applications and Flatpak updates have separate ownership; see
[application updates](app-sources.md#update-ownership). The daily monitor reports
available updates but does not establish unattended-update compliance.

Configure an employer-approved independent backup destination, retention and
schedule, then test restoration. `restic` being installed does not mean a backup
repository or job exists. Include work data and privately recoverable VPN and
account material according to policy.

## 16. Final acceptance and later Secure Boot work

The laptop is ready for daily work only when these required gates pass:

- [ ] Encrypted boot, graphical login and reliable lock/unlock.
- [ ] Stable XPS GPUs, KVM/displays and suspend/resume.
- [ ] Working work-only VPN, DNS, internal services and Git access.
- [ ] Required browser/SSO/password-manager access.
- [ ] Slack notifications and a real Zoom audio/video/sharing test.
- [ ] Representative project build/test/debug workflow.
- [ ] No unexplained failed services or desktop configuration errors.
- [ ] Repeat provisioning preserves local configuration.
- [ ] Independent backup restoration and a usable OS recovery plan.
- [ ] Update/reboot checks recorded, including whether a newer kernel was tested.
- [ ] Employer security requirements, including the separately unresolved Drata
  requirement, are satisfied. Do not mark complete based only on package launch.

Secure Boot is a later project unless employer policy makes it mandatory now.
Keep it disabled with the current candidate. Adding it later need not repartition
the disk, but requires a reviewed signing/enrollment/update pipeline, revised
Hexen audits and tested recovery. Do not just flip the firmware toggle.
See [Secure Boot follow-up](xps-14-9440.md#secure-boot-follow-up).

## Stop points

| Symptom | Next action |
| --- | --- |
| No eligible blank disk | Inspect actual disk state; the wrapper does not wipe it. |
| Unsupported Archinstall version | Use compatible media; preserve the version guard. |
| Failed download/signature/package transaction | Preserve the error, verify networking/time/source; do not weaken signature checks. |
| First boot/provisioning fails | Keep the terminal output, investigate, then use the documented retry path. |
| Graphical login or external screens fail | Try the panel/TTY, inspect GPU and SDDM state; do not immediately reinstall. |
| VPN imports but work access fails | Check MFA, dependent files, DNS/routes and employer instructions on this work laptop. |
| Update fails | Preserve the checkpoint/log and investigate before rebooting or rerunning blindly. |
| Installed OS cannot boot | Use recovery media and the matching root/EFI recovery procedure. |

Keep this runbook and the [prioritized checklist](work-laptop-checklist.md)
available on another device. This document is local until explicitly committed
and published; it is not automatically included in the pinned candidate archive.
