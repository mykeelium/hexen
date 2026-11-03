# XPS Hybrid Graphics Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Provide an opt-in, validated XPS 14 9440 installation/provisioning path.
**Architecture:** A standalone sysfs checker gates an explicit hardware profile;
wrappers propagate it and Ansible installs driver/session configuration.
**Tech Stack:** Python stdlib, Bash, Ansible, udev, UWSM.
**Spec:** ../specs/2026-11-03-xps-hybrid-design.md

## Global constraints
- Keep generic VM behavior and existing local source edits.
- Only XPS 14 9440 + 8086:7d55 + 10de:28a1; Secure Boot deferred.
- Never select or erase a disk automatically; no live GPU rebinding.
- No claim of physical hardware acceptance from VM tests.

## Review focus
- Wrong GPU/model, unreadable firmware state: fail before mutations.
- CLI and saved-profile conflicts: validate and preserve selected hardware.
- Existing UWSM files: preserve unrelated settings; refuse unsafe symlinks.
- Kernel/driver packages: standard linux and matching repository module/userspace.
- Card numbering/monitor names: use stable DRM aliases, leave layout local.

## Tasks
1. Write failing fixture tests for standalone hardware preflight and refusal
   cases; implement install/hardware.py and make fixture tests pass.
2. Add failing wrapper/installer profile tests; propagate --hardware through
   first boot, provisioning and generated install; persist selection and validate
   before mutations. Existing commands without --hardware retain generic behavior.
3. Add isolated Ansible coverage; implement opt-in driver packages, DRM aliases,
   UWSM fragment and saved profile. Verify second run makes no changes.
4. Incorporate the demonstrated test-only timing correction, add CI coverage for
   hardware tests/dependencies, and write XPS installation/backup/hardware gates.
5. Run the full suite, Arch wrappers and Ansible fixtures; review changes and
   document physical checks that remain. Do not publish or install on laptop.

## Outcome

Tasks 1–5 implemented and verified; see ../../xps-validation-2026-11-03.md.
Ruling: keep the current branch as authorized earlier; preserve the existing
user test correction. No source commit/publication or laptop installation was
performed. Physical acceptance and blank-disk preparation remain owner gates.
Ruling: use a successful initramfs signature rather than a change-only trigger;
the review found that a failed rebuild must retry on unchanged subsequent runs.
