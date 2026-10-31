# Guided Archinstall Design

## Intent

Give a new Hexen user a guided first-install command that prepares an
Archinstall configuration from explicit machine inputs, then launches
Archinstall to perform the install. This reduces repeated menu work while
keeping destructive actions and credentials visible to the person at the
machine.

## Goals

- Build the Hexen base-install configuration from the supported choices in
  `install/archinstall/choices.md`.
- Require an explicit runtime disk selection; never default to a disk path or
  reuse a saved disk layout.
- Show a complete summary, including the selected disk identity and that it
  will be erased, before launching Archinstall.
- Keep the final Archinstall review and install confirmation interactive.
- Keep LUKS and user passwords out of the generated configuration, command
  arguments, repository, and persistent Hexen files. The handoff collects
  credentials through hidden prompts and supplies them to Archinstall in memory.
- Use a temporary generated config and remove it when the command exits.
- Guide the user to first-boot Hexen provisioning after the base install.

## Non-goals

- Building or publishing a custom ISO.
- Supporting BIOS, Secure Boot, multi-disk layouts, dual boot, RAID, LVM, or
  arbitrary existing partitions in the first version.
- Automatically rebooting, signing in, cloning private credentials, or running
  the post-install Ansible playbook from the live installer.

## Constraints

- First version targets the documented x86_64 UEFI, GPT, single blank disk,
  LUKS2, Btrfs, and Limine setup.
- Runtime inputs include target disk, hostname, username, timezone, locale,
  and mirror region. The account password and encryption passphrase are entered
  through hidden interactive prompts and can be reviewed in Archinstall.
- The generated layout must match the current documented ESP and Btrfs
  subvolume choices; it must not reuse the rehearsal VM's `/dev/vda` path.
- The script must fail closed when required commands, UEFI mode, network, or a
  validated Archinstall configuration version are absent.
- The initial implementation will be accepted only after a disposable VM run
  confirms the generated configuration, Archinstall's credential prompts and
  final confirmation, encrypted boot, and first login.

## Approaches

1. Keep the current hand-maintained menu walkthrough. This is simplest and
   avoids configuration-schema compatibility work, but it does not meet the
   request to generate a configuration.
2. Generate a temporary Archinstall JSON configuration from the supported
   choices and explicit machine inputs, then invoke the official guided
   installer with that configuration. **Selected:** this cuts down repeated
   menu selection while retaining Archinstall's review and destructive-action
   confirmation.
3. Create a custom ISO with a Hexen installer environment. This could make
   startup smoother, but adds ISO build, release, and maintenance work before
   the generated configuration is validated.

## Proposed flow

1. Run the command from the official Arch live ISO in a UEFI boot, from a
   checked-out Hexen repository.
2. Check architecture, required tools, installer version, UEFI mode, and
   network access. Stop with a clear explanation if the machine is outside the
   supported scope.
3. Display available whole-disk devices using model, size, transport, and
   mount status. Require a user selection and explicit typed confirmation of
   the chosen disk before generating the layout.
4. Ask for hostname, username, locale, timezone, and mirror region; show
   defaults from the documented choices where they are safe and applicable.
5. Write the non-secret Archinstall configuration in a private temporary
   location, show the exact plan and disk-erasure warning, then run
   `archinstall` with the config in interactive mode. Do not pass a credentials
   file.
6. Remove the generated temporary file on exit. After Archinstall returns,
   show first-boot checks and the separate Hexen provisioning command.

## Open implementation details

- Confirm which Archinstall version and JSON schema are accepted by the live
  ISO used for the VM rehearsal. Abort on unvalidated versions instead of
  guessing that a saved schema remains compatible.
- Confirm how the selected Archinstall release prompts for credentials when a
  non-silent configuration omits the credentials file, and where any generated
  credential data is stored, so the workflow does not leave credentials on the
  installed disk.
- Validate how Archinstall identifies a selected disk when passed in the
  generated configuration; display and confirm the exact value it will use.

## Decision

The user selected configuration generation. The proposed first release is a
small shell entry point for the currently supported single-disk UEFI install;
the user approved this design on 2026-10-30.

Implementation finding: Archinstall 4.5 drops encryption settings when no
password is supplied during config parsing. The version-specific adapter
therefore attaches disk encryption and account credentials in memory before
opening the guided menu. The shell command defaults to preview; --install
enables the experimental handoff. A fresh VM installation remains required.
