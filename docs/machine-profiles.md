# Machine software profiles

The first profile layer handles software package additions only. The existing
base, apps, and desktop package lists remain the shared `common` set. The
selected tracked profile can add packages to those lists, and an ignored local
override can append private machine-specific packages last:

```text
common packages → selected profile additions → ignored local additions
```

The default profile is `common`. To select a tracked profile on one machine,
create or edit the ignored file `ansible/group_vars/all/local.yml`:

```yaml
hexen_machine_profile: arcana
```

Merge this setting into that file if it already contains other local settings;
do not replace existing machine-specific entries.

Tracked profile files live in `ansible/profiles/` and currently include
`common`, `numen`, and `arcana`. Their package lists are empty until concrete
software differences are selected. This avoids assigning hardware-specific
choices to a machine before its inventory is known.

Local software additions use only the appropriate package category:

```yaml
hexen_profile_local_overrides:
  apps:
    - example-package
```

The supported categories are `base`, `apps`, and `desktop`; each value must be a
list. Profile and local package additions are appended to the common packages
and installed from the roles' existing Arch package managers. Review every
package and its source before applying. This first version only adds packages;
it does not remove a common package through a profile. Switching profiles also
does not uninstall packages that an earlier profile added.

Credentials and other private values must not go into the tracked profile
files. Monitor, GPU, input, network, and other hardware settings remain outside
this software-only layer until the target machines are inventoried. Config file
overlays remain later roadmap work.

## Inspecting changes

After desktop provisioning installs the command, use:

```sh
hexen config status
hexen config diff
hexen config apply
hexen config backup hypr
hexen config restore BACKUP_ID
```

`status` reports the selected profile, repository revision and dirty state, and
whether expected desktop symlinks are missing or point somewhere else. A dirty
repository is informational; missing or unexpected managed links produce a
nonzero exit status. `diff` shows staged and unstaged changes and the contents
of untracked, non-ignored regular files. It does not modify the repository or
the home directory.

`apply` launches the existing interactive `install/provision.sh` path. It
reports the selected profile, then delegates the impact summary and
confirmation prompt to that script; it does not start Ansible in
non-interactive mode. Use `hexen config apply --vm` for the documented
nested-VM settings. The provisioner still checks Ansible syntax, asks before
applying changes, prompts for the desktop launcher, and requests privilege
authorization when needed.

`backup PATH` copies one file or directory from `~/.config/` or the repository's
`config/` tree into a new private directory under
`$XDG_STATE_HOME/hexen/backups/config/` (default `~/.local/state/...`). A
relative path such as `hypr` means `~/.config/hypr`; a path beginning with
`config/` is relative to the repository. Symlinks that resolve inside either
allowed config tree are backed up as their resolved content. Paths outside
those trees, unsafe backup directories, and replacing an existing backup are
refused. Backups are not encrypted or copied off-device; do not use this as a
credential backup.

`restore BACKUP_ID` accepts only IDs created by `backup`. It requires an
interactive confirmation and restores only to the original path inside
`config/` or `~/.config/`. It refuses symlinked destinations, changed path
types, and missing parent directories. If the destination already exists,
Hexen first creates a new safety backup and then replaces it. Directory
restores are staged beside the destination before replacement. Review the
printed destination before confirming.

## Checking update status

`hexen update --check` is a read-only report. It compares the checkout with
its configured upstream using the most recently fetched remote-tracking data,
lists packages shown by the local Pacman sync database, checks whether the
running kernel's module tree is present and whether another module tree appears
newer than boot, and reports managed links that need reconciliation. It does
not fetch Git data, refresh package databases, install packages, or change
configuration. Package results may be stale; the report shows the sync
database's timestamp and warns when it is over 24 hours old. The kernel result
is only a reboot signal, not a complete service-restart analysis. Run the usual
service/update review. `hexen update` is the separate interactive transaction
entry point described below.

`hexen update-monitor` (also installed as a daily systemd **user** timer) checks
official Arch updates with `checkupdates` in its separate per-user package
database. It does not refresh Pacman's system database, download packages, or
install anything. Private timestamped Markdown reports and JSONL check,
notification, and owner-decision records live under
`~/.local/state/hexen/updates/`; `latest.md` is the newest report. Open that
report to review package versions, repository names, Arch package pages, and
packaging-recipe history, then run `hexen update` in a terminal if you decide
to apply updates. Notifications never start the update transaction. The user
timer runs when the user's systemd manager is active; if the machine was off,
`Persistent=true` catches up when the manager next starts. A failed or offline
check is reported as unknown, not as current. If desktop notifications are
unavailable, the report and evidence are still saved.

Run `hexen update-monitor review` in a terminal to refresh discovery and walk
through each available package. For each one, record it as reviewed, wanted for
the upcoming update, follow-up, or undecided. The package page and Arch recipe
history links are shown with installed/candidate versions and repository. Each
choice is appended immediately to the private evidence log, so quitting or
interrupting preserves completed decisions. The final summary offers an
explicit handoff to `hexen update` or cancellation. Handoff is not transaction
approval: `hexen update` still asks separately before source changes, snapshot
creation, and the full `pacman -Syu` transaction. Package flags are review
notes; they cannot restrict the transaction to a subset because Arch does not
support partial system upgrades. A richer TUI can later use the same review
state and evidence functions; this first interface uses standard terminal
prompts and adds no UI dependency. On the nested rehearsal VM, pass
`--vm` (`hexen update-monitor review --vm`) so optional Ansible convergence
uses the VM network settings.

After a successful package transaction, the update checkpoint includes a
package delta and, when old/new archives remain in Pacman's cache, SHA-256,
`.PKGINFO`, `.BUILDINFO`, file inventories, and a file-list diff. Missing old
archives or metadata are recorded as “not compared.” The Pacman transcript is
the record of repository and signature output; review it per package. A valid
signature establishes signer trust for an artifact, not that its sources or
build are harmless. Flatpak, AUR/vendor, AppImage, Walker/Elephant, Neovim,
and language-tool updates remain outside this Arch-package monitor.

The monitor records scheduled discovery and whether the owner approved or
declined a transaction. It does not install unattended updates. Confirm with
the employer that this scheduled detection and owner-approved response meets
its automatic-update policy; this workflow cannot claim compliance when policy
requires unattended installation.

`hexen update` currently performs the first, checkpointed Arch package-update
slice. It requires a terminal, a clean repository checkout, the supported
Btrfs root/Snapper setup, and a mounted FAT ESP at `/boot`. A checkout already
known to be diverged from its cached upstream is refused; incoming upstream
commits are fetched and offered for review. It refuses an existing Pacman lock
and requires `/home` to be a separate Btrfs subvolume, as in the documented
install layout. It checks that `/home` can hold a copy of `/boot` and that
`/boot` has room at least equal to its current file contents (or 64 MiB). After
showing free space and the recovery boundary, it creates a private preflight
log under `~/recovery/hexen-updates/`, falling back to
`~/.local/state/hexen/updates/checkpoints/` when the recovery parent is not
writable by the user. It requires confirmation before it fetches the
configured Git remote. Incoming commits and their full diff are shown; a
separate confirmation is required before a clean fast-forward, which immediately
updates source-linked configs. Diverged branches stop the workflow. The previous
and resulting source revisions are recorded in `source-revisions.txt` for
manual recovery.

After that review, Hexen records package/mount/subvolume data, creates a Snapper
root snapshot and matching `/boot` archive with checksums. It reads `/boot`
through `sudo` and streams the archive into a private file owned by the logged-in
user. It then runs one
interactive `sudo pacman -Syu` transaction. It records before/after package
manifests, `.pacnew`/`.pacsave` candidates, failed system units, and a limited
kernel reboot signal. After a successful transaction and package manifest, it
offers any reviewed user migrations as a separate, explicitly confirmed step.
They run as the logged-in user, never during Pacman or as root. `hexen migrate`
can run pending work later. If migrations are complete, Hexen offers a separate
Ansible configuration review. The provisioner runs syntax validation and
check/diff mode, then asks again before applying the full playbook. Check mode
is advisory: command-based tasks may be skipped or may not predict their full
effect. Use `hexen update --vm` for nested-VM network settings; default
convergence uses workstation settings. The transcript, convergence result,
post-convergence package manifest, and failed-unit list are stored in the same
recovery directory. A read-only source report records the LocalSend pin/hash
match, installed versions of separately managed packages, Bitwarden's installed
Flatpak version, Hyprmon binary presence, and the tracked Neovim pin count. It
does not query upstreams or claim those sources are current. If
`archlinux-contrib` is installed, Hexen offers `checkservices -P`, which skips
`pacdiff`, reloads systemd as needed, and asks before each service restart.
Post-convergence package/unit records are captured after the provisioner starts,
whether or not the apply confirmation is accepted. Hexen does not reboot
automatically. Manual application sources remain separately owned.

Failed transactions retain the checkpoint and log. Hexen never reboots or rolls
the system back automatically. After a failed package transaction, inspect the
log and package state, then choose whether to retry or use the documented
offline recovery procedure. Close other package managers before proceeding.
Hexen checks the Pacman lock before and during checkpoint creation and compares
package manifests, but it does not install an ALPM guard; normal package tools
do not honor Hexen's per-user lock.

Migrations are listed in `install/migrations/manifest.json` and implemented as
numbered Python files beside it. IDs are immutable once released; scripts must
be safe to retry because a process can stop after making a change but before
Hexen records completion. Successful migrations receive private per-user
markers under `${XDG_STATE_HOME:-~/.local/state}/hexen/migrations/`. Standalone
`hexen migrate` logs go under that state directory's `logs/`; update-triggered
migration output is appended to that update's recovery log. A failed migration
remains pending, while earlier successful migrations stay complete. The
current manifest is empty, so no migration is defined or run. Review migration
source changes with the repository update.

The root snapshot does not include `/home`. Restore system files from the
Snapper snapshot and restore `/boot` from that same run directory as a pair.
The repository checkout and its managed home configuration live under `/home`;
if the update fast-forwarded source and you need to restore it, first confirm
the checkout is clean, then return it to the recorded `before` revision and run
`hexen config apply`:

```sh
git status --short
git reset --hard <before-revision>
hexen config apply
```

Run `git reset --hard` only when `git status --short` is empty. Restore personal
files from a separate backup. Local
update checkpoints are not an off-device backup and are retained for manual
review/cleanup. Hexen does not automatically update separately owned
applications, issue a reboot, or claim that service restarts are unnecessary.
Review the checkpoint and the [application update ownership table](app-sources.md#update-ownership)
for Flatpak, pinned AppImage, AUR, Walker, Hyprmon, and Neovim update paths.

## Edit and share

1. Check the selected profile and current repository state:

   ```sh
   hexen config status
   ```

2. Edit a shared file either in the repository or through its managed link in
   `~/.config/`. For example, `~/.config/hypr/bindings.lua` points to
   `config/hypr/bindings.lua`; edits through either path change the same tracked
   file. Put shared desktop behavior and the inclusive package set in common
   files.

3. Put a tracked software difference in the selected file under
   `ansible/profiles/`. For a package that belongs only on this machine, use
   `hexen_profile_local_overrides` in ignored `ansible/group_vars/all/local.yml`.
   Put a private compositor override in the ignored `config/hypr/local.lua`.
   Keep passwords, tokens, private keys, and recovery codes in the approved
   credential store, not in configuration files.

4. Review all changes before applying or sharing them:

   ```sh
   hexen config diff
   git diff --check
   ```

   Validate the affected config with its documented checker. For live Hyprland
   edits, run `hyprctl reload` and `hyprctl configerrors`. For Ansible changes,
   run the syntax check from the repository root:

   ```sh
   ANSIBLE_CONFIG=ansible/ansible.cfg \
     ansible-playbook --syntax-check \
     -i ansible/inventory/localhost.yml ansible/playbook.yml
   ```

5. Stage only the reviewed files, inspect the staged diff, and commit them:

   ```sh
   git add path/to/reviewed-file
   git diff --cached
   git commit -m "Describe the configuration change"
   git rev-parse --short HEAD
   ```

   Avoid `git add -A` when other work is present. `hexen config diff` shows
   staged and unstaged tracked changes and untracked, non-ignored file contents.

6. Make the reviewed commit available from the configured Git remote. On the
   other machine, require a clean working tree first; if `git status --short`
   reports changes, stop and review, commit, or stash them before updating.
   Fetch, fast-forward to the exact reviewed commit, recreate that machine's
   ignored profile selection if needed, then inspect and apply:

   ```sh
   git status --short
   git fetch
   reviewed_commit=abc1234
   git merge --ff-only "$reviewed_commit"
   git rev-parse --short HEAD
   hexen config status
   hexen config apply
   ```

   `apply` shows the target and source state, then the provisioner asks before
   making system changes. Review the result and run `hexen config status` again.
   The ignored local settings do not travel with Git; reproduce only the
   machine-specific values needed on that machine.
