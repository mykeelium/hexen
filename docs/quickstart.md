# Hexen developer preview: start here

This preview is for a disposable VM. The generated installer has not yet passed
a complete fresh-install rehearsal. Hardware compatibility and newer-kernel
upgrade acceptance remain open. See [known issues](known-issues.md).

## What you need

- An x86_64 UEFI VM with Secure Boot disabled, at least 4 GiB RAM (8 GiB recommended for source builds) and a new blank
  disk of at least 40 GiB. Do not attach disks containing data you need.
- Official Arch installation media with **Archinstall 4.5**. The recorded
  rehearsal ISO is 2026.10.01. Other installer versions are refused.
- A US keyboard layout. Other layouts are not yet supported by the generated
  preview; the desktop currently uses US regardless of the console layout.
- Internet access throughout setup; package builds can take substantial time
  and disk space. Wi-Fi must be connected before running the installer.
- The account password and encryption passphrase you choose, retained outside
  the VM. They are separate passwords with separate purposes.

## 1. Start from the live ISO

Download and verify the official media using https://archlinux.org/download/.
Boot the VM from that ISO in UEFI mode. Connect networking before continuing;
for Wi-Fi use `iwctl` from the live shell. Check `ip address` and
`curl -I https://archlinux.org` if the connection fails.

From the live ISO's root shell:

```sh
curl -fL --retry 3 -o /tmp/hexen-source.tar.gz https://github.com/mykeelium/hexen/archive/refs/heads/main.tar.gz
bsdtar -xf /tmp/hexen-source.tar.gz
cd hexen-main
./install/archinstall/hexen-install.sh
```

Git is not required in the live ISO. This archive URL must be publicly accessible
before release; the configured repository is currently private. Until a tested release tag is published, this downloads
development source. Do not
assume every commit has installation acceptance. Once a release exists, download
the archive for the exact release tag named in its notes before running setup.

The command previews the plan. It never chooses a disk for you. For a fresh
blank VM disk, launch installation with:

```sh
./install/archinstall/hexen-install.sh --install
```

Read the erase confirmation and enter the selected disk path exactly when
prompted. Password entry is hidden; no asterisks appearing is normal. Review
Disk encryption, Authentication, Limine, and the entire plan inside Archinstall
before choosing Install. Keep the keyboard layout set to US in Archinstall.
Do not select Save credentials. Mirror checks, keyring
synchronization, encryption setup, package downloads and source builds can take
several minutes; read the current progress before restarting the installer.
If installation fails after disk changes, stop and inspect the error. This
preview does not resume or automatically wipe a partially installed disk. Use
a new disposable disk for another full rehearsal. Never disable package
signature verification to bypass a download or database error.

## 2. Boot the installed system

After installation succeeds, exit Archinstall, reboot, and boot the installed
disk instead of the ISO. Enter the disk passphrase. Log into the shell with
your new username and account password. A shell login at this stage is expected:
Hexen installs its graphical login during the next stage.

Check that the installed system is online before cloning. A wired VM normally
connects automatically. If Wi-Fi needs reconnecting, run `nmtui`, choose
**Activate a connection**, select your network, and enter its password. Quit
`nmtui`, then check the connection with `curl -I https://archlinux.org`.

Verify encrypted Btrfs boot using [the boot checks](../install/archinstall/README.md#verify-after-first-boot).
Then clone the repository again onto the installed disk; the live ISO checkout
was temporary:

```sh
git clone https://github.com/mykeelium/hexen.git "$HOME/hexen"
cd "$HOME/hexen"
./install/first-boot.sh --vm
```

Use the same tested release revision in both stages. Release notes must give
the exact branch/checkout commands: a detached tag checkout skips reviewed
source updates, so the installed checkout needs a local branch with an upstream.
The `--vm` command must run inside the target VM; it refuses a detected physical
host. Keep this checkout in place; desktop configuration links point into it.

The command asks whether to use Walker or Fuzzel. Fuzzel comes from the official
Arch repositories. For Walker, it installs build tools and the documented
official dependencies, then guides you through review
of each pinned Walker/Elephant recipe and built archive, then runs Ansible.
In the recipe pager, scroll to read and press `q` to leave. Approve only recipes
you are comfortable executing. On a retry, you can explicitly reuse already installed Walker packages after
checking the displayed versions. Reuse only providers built together with
Elephant using the same Go toolchain. Sudo and Ansible's `BECOME password` both mean
your account password. The selected launcher is passed to provisioning.
Official package transactions and each third-party build/install require review.

## 3. Sign into Hexen

After setup succeeds, reboot, unlock the disk, and sign in at the graphical
login (SDDM). On the first sign-in, select **Hyprland (UWSM-managed)**
in the session selector. Open the selected launcher with Super+Space. Super+Shift+B opens Zen if installed,
otherwise Firefox. See [desktop shortcuts](desktop.md).

If setup stopped, keep the terminal open, read the error, correct it, and rerun
the same first-boot command. It must not be run as root. It can perform a full
system upgrade on each run; use the [maintenance workflow](maintenance.md) for
routine updates after installation. A failed provisioning
run can leave partial changes; do not treat an error as a completed setup.
For read-only checks, run `python3 install/health.py` from the checkout.

Zen, 1Password, Zoom, Slack, and Hyprmon still have separate reviewed install
procedures in [manual applications](../install/manual-apps/README.md). Bitwarden
is installed from Flathub. Account sign-ins are yours to perform.

## Getting help

Report the release/commit, ISO and Archinstall version, exact failed stage, and
error message. Review any log before sharing it. Never attach passwords, tokens,
private keys, `user_credentials.json`, or entire installer log directories.
See [recovery](recovery.md) before attempting disk or snapshot repairs.
