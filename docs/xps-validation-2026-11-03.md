# XPS profile implementation verification — 2026-11-03

This records software verification of the working-tree implementation based on
`140e239a40fd33a867bf9fd4901716eebb1cbfdd`; it is not a published candidate or
physical XPS acceptance. The owner's existing desktop-helper test correction was
preserved. The opt-in target is XPS 14 9440 + Intel 8086:7d55 + NVIDIA 10de:28a1.
Secure Boot remains deferred.

## Verified software

- Read-only hardware fixture tests cover model/GPU/UEFI/Secure Boot refusal,
  saved-selection reuse, unsafe/downgrade/VM conflicts, kernel-version matching,
  and post-reboot DRM alias/modesetting checks.
- Real interactive wrapper tests cover XPS first-boot package propagation and
  refusal before package mutations; generic and VM paths retain their flags.
- Isolated Ansible tests create only disposable configuration trees. They cover
  generic behavior, XPS file creation and idempotence, preserved unrelated UWSM
  settings, unsafe symlink/unmanaged-file refusal, and failed initramfs rebuild
  followed by successful retry and an unchanged third run.
- Full host suite: 96 passed, no skips (Python 3.11 with test dependencies,
  Ansible 2.19.15, Unix socket access).
- Full suite inside installed Arch rehearsal VM: 96 passed, no skips (Python
  3.14, Ansible 2.22.0, Pillow 13.0.0, FontTools 4.68.0 in temporary test venv).
- Ansible playbook syntax, Bash syntax and git diff whitespace checks passed.
- Independent review found a failed-rebuild retry issue; the success-signature
  implementation and failure/retry test resolved it. Follow-up review found no
  further concrete issues.

The VM received a source-only archive, SHA-256
`4990133edec4dc864bfda0f199529362e04d6d20655b36cfdf6b04f707de1b03`.
The archive precedes this evidence note. A temporary bridge HTTP transfer timed
out and was stopped; serial transfer produced the matching hash. No firewall
exceptions or guest remote-access packages were added.

## Installed generic VM regression

The reviewed source snapshot was applied in the existing disposable Fuzzel VM's
permanent checkout, preserving the previous source archive for reference. This
checkout now contains the implementation as working-tree changes; it must not be
mistaken for a clean published candidate at the old HEAD.

First real provisioning: `ok=187 changed=1 failed=0`; the sole change recorded the
new `generic` hardware selection. Repeat: `ok=190 changed=0 failed=0`. The second
run reads the saved setting and remains idempotent. Health passed, no failed
system/user units were reported, Tokyo Night theme preview was unchanged, HTTPS
returned 200, and no XPS udev/modprobe configuration or `nvidia-open` module package appeared.
`nvidia-utils` was already present: the Pacman log records its installation at
08:14:35, during the original setup, before this implementation regression. No
package-install task changed during this regression.
Existing VM defaults and launcher behavior were preserved.

## Remaining gates

- Commit/review/publish the implementation and require all CI jobs to pass for
  that exact new revision; downloads of the old base commit omit these changes.
- Run the read-only checker on the actual Mint XPS/UEFI live media, then validate
  a graphical environment using the intended NVIDIA/Hyprland stack before disk
  replacement. VM tests do not validate this machine's MST/KVM/power behavior.
- Restore from independent backup, test Zoom/Slack/Firefox/Go work scenarios,
  perform a second-person walkthrough, and accept a newer-kernel transition.
- The blank-disk-only installer still refuses the occupied Mint disk; no wipe,
  in-place migration, dual-boot or Secure Boot support is added here.

See [the XPS installation guide](xps-14-9440.md) for ordered owner-side gates.
