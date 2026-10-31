# Generated installer rehearsal — 2026-10-30

Status: base installation, LUKS2 encrypted reboot and synthetic-account login
passed with an assisted mirror retry. First-boot setup and a zero-change provisioning rerun passed;
this is not complete installation acceptance.

## Isolated environment

- New VM: `hexen-installer-preview-20261030`; existing installed VMs untouched.
- New disposable 64 GiB Virtio disk, UEFI, Secure Boot disabled, 4 GiB memory.
- Existing official Arch ISO boots kernel 7.2.7 and reports Archinstall 4.5.
- Synthetic hostname `hexen-preview`, account `betauser`. No owner credentials
  were used; synthetic test passwords are not release defaults.
- Unpublished source copied to live media for testing; no release commit/tag
  exists for these working-tree changes.

## Findings corrected in source

- Plymouth must be unset/null; false fails the installed parser.
- ESP needs explicit `esp` as well as `boot` flags for the installed validator.
- Encryption is dropped by config parsing without a passphrase; the adapter
  attaches it in memory and final disk operations require unchanged layout.
- First-boot Firefox prerequisites need an explicit PipeWire JACK provider to
  avoid an unexpected JACK2 selection prompt before desktop provisioning.
- The adapter preserves upstream package-database initialization and font
  lifecycle, and applies the requested keymap before password entry.
- Region codes must resolve to country names. More importantly, Archinstall's
  region handling ignores supplied URL subsets and probes the entire region,
  including HTTP. The final generator now passes explicit selected HTTPS
  servers, sorted by status score, instead.
- A mounted source ISO at /mnt conflicts with Archinstall staging. The test
  source was copied into RAM and unmounted; production preflight now refuses
  an already mounted /mnt.
- SDDM is checked as enabled before first reboot; requiring it active would
  falsely report a provisioning failure before the intended reboot.

## Observations

The real ISO parser accepted the partition geometry, Limine, NetworkManager,
encrypted Btrfs and synthetic sudo account. The interactive wizard collected
values/passwords and opened the upstream menu. The final review/confirmation
was exercised. The adapter created a FAT32 ESP and LUKS2 Btrfs system partition,
then mounted the default subvolumes.

The first package download produced a truncated extra.db archive. Its dependency
errors were secondary to that archive corruption. Only the disposable live
VM's mirror list and target's two downloaded DB caches were replaced/cleared,
then Archinstall's package-download retry was used. This assisted retry must
not be reported as an uninterrupted successful run of the final generator.
No package signature checks were disabled.

## Acceptance still required

- [x] Complete package installation, boot Limine, unlock LUKS2, and log in as
  betauser. Verified kernel 7.2.11, UID 1000/wheel, Btrfs /dev/mapper/root[/@],
  and active NetworkManager.
- Rehearse the final explicit-HTTPS mirror configuration from start to finish.
- [x] Run the new first-boot prerequisites and reviewed Walker builds as the
  regular account. Walker 2.17.2 and Elephant/six providers 2.22.1 built and
  installed. Initial provisioning reported ok=190 changed=48 failed=0; final
  source rerun reported ok=183 changed=0 failed=0. Basic health checks passed. The staged helper also installed
  optional debug archives; final source now selects only the requested package
  archive, with focused regression coverage.
- [x] Post-provisioning reboot reached SDDM with the betauser account and
  UWSM-managed Hyprland selected. Managed Hyprland launched; Walker app search
  and 1+1 -> 2 worked. Google search opened the synthetic phrase in Firefox.
  Both normal and private browser shortcuts opened the expected Firefox modes.
  HTTPS default handler is firefox.desktop, and hexen-elephant.service is active.
- Exercise health report, repeat provisioning, updates and recovery.
- Test the published commit/tag using only the public quickstart.

## Source regression checks

The complete Python suite passes: 51 tests with temporary Unix socket binding
allowed. The ordinary sandbox denies socket binding, causing 14 controller
fixture failures unrelated to screensaver behavior. The remaining baseline
firewall test failure was fixed by rendering the Jinja template with its real
defaults before parsing XML; an additional test covers explicit IPv4/IPv6 SSH
source rules. The production firewall policy itself was unchanged.

Publication check: GitHub API confirms mykeelium/hexen is PRIVATE with default
branch main. No visibility changes, commits, tags or publication were made.
The live ISO lacks Git, so the public live-media instructions now use a source
archive download; installed-system setup uses Git after the base install.

Post-reboot firewall: default/active drop zone, target DROP, only dhcpv6-client
service, no ports, protocols, forwarding, masquerading or rich rules. This does
not replace external-network/hardware firewall acceptance.

Final first-boot guard rejects --vm on the physical development host before
any package transaction; the guest correctly reports KVM. The health report
recognizes an already active graphical login and does not request another reboot.
