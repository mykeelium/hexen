# Generated Archinstall configuration implementation plan

**Goal:** implement the approved guided configuration generator.
**Spec:** ../specs/2026-10-30-guided-archinstall-design.md
**Architecture:** shell entry point, standard-library Python wizard and version-specific in-memory Archinstall adapter. No stored credentials. No automatic reboot or provisioning.

- [x] Add focused tests for disk refusal, partition geometry, encryption selection, and secret-free output; observe failures first.
- [x] Implement configuration generation and runtime preflight for official x86_64 UEFI Arch media and Archinstall 4.5.
- [x] Implement the interactive Archinstall handoff, ensuring encryption survives config parsing without a credentials file.
- [x] Document invocation and experimental status; run focused tests and syntax checks.
- [ ] Rehearse on a new disposable VM before marking installation accepted. Never reuse an installed VM disk for this check.

Ruling: upstream 4.5 drops encryption during parsing without a password. Use its Python API to attach encryption in memory before the guided menu. Upstream save() defaults to creds=False; do not invoke Save credentials.

Validation: two focused unittest cases pass; shell syntax and --help checks pass; git diff --check is clean. Upstream 4.5 source reviewed for parser, encryption and credential persistence behavior. No disk operations or VM installation were performed. Existing user documentation changes were preserved. No commits created.

Review: corrected handoff to preserve upstream entry initialization and console font lifecycle; selected keyboard is loaded before password entry. These runtime paths still require live-media rehearsal.
