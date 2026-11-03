# Rehearsal preflight — 2026-11-02

This is source preparation evidence, not installation acceptance. No VM was
installed or existing system disk changed during these checks.

## Source access

- GitHub API reports `mykeelium/hexen` is public with default branch `main`.
- An anonymous HTTPS download (without GitHub credentials) returned HTTP 200
  for commit `33749817b6913a5ba617b278275e2238c9e63347`.
- The downloaded tarball contains 309 entries under
  `hexen-33749817b6913a5ba617b278275e2238c9e63347/`, including the generated
  install entry point. This verifies the full-commit archive directory naming
  used by the quickstart.
- Observed archive SHA-256:
  `a8aecd7171d3742643ec1ee7cfb229202378833c1919419376577ec8ebaf34d9`.
  This is an observation for that download, not a release signature or a promise
  that GitHub will reproduce identical archive bytes indefinitely.
- No repository visibility changes, pushes or release tags were performed.

The checked commit predates the pending readiness and theme-regeneration fixes.
Those changes are uncommitted and were not included in the download. Repeat
access and source checks for the final committed candidate before rehearsal.

## Local verification and review boundaries

- The preceding implementation pass ran 77 Python tests successfully, including
  real Ansible task dispatch against a temporary checkout/home and fake Matugen.
  Full playbook syntax validation also passed. These are working-tree results.
- CI now has a dedicated theme-sync job with Ansible Core 2.19.15 so the task
  integration case is available without depending on runner-installed tooling.
  Its exact shell commands were executed locally in a fresh temporary virtual
  environment: all 15 theme tests passed, including Ansible integration. This
  is not evidence that the job has run on GitHub for the final candidate.
- Workflow YAML and shell-block syntax, changed documentation file links, and
  whitespace checks passed. A read-only review found no actionable issues in
  this preflight increment.
- Tracked-filename inspection found no VM disk/ISO files, credential exports,
  private-key filenames or machine-local override files in the checked set.
- A limited non-document source scan found no matches for private-key headers,
  GitHub-token patterns or AWS access-key-ID patterns. It did not establish
  that every file is free of private data. Review tracked/untracked contents
  before committing; the release privacy gate remains open.
- Third-party asset inventory remains incomplete. Source access is not asset
  clearance; preserve notices and finish that review before a public release.

## Remaining preparation

- [ ] Review and commit the intended changes without machine-local files.
- [ ] Run required local checks and GitHub jobs for that exact commit; record
  skipped checks and limitations.
- [ ] Repeat anonymous archive access for that commit and confirm both install
  stages select it.
- [ ] Have verified Arch media with Archinstall 4.5, a blank disposable VM disk,
  synthetic account details and the candidate acceptance checklist available.
- [ ] Record ISO and installed package versions; the source commit does not pin
  Arch's rolling repositories.

The VM rehearsal exercises the installed behavior. It does not establish
physical-machine profiles, independent backup restoration, work-account access,
VPN/VM networking or meeting-workflow acceptance; those workstation gates remain
in the operations roadmap. Scheduled discovery of Hexen repository commits is
also still unimplemented; the existing update path fetches source interactively.
