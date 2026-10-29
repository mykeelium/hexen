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
