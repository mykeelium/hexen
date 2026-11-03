# Developer preview release checklist

For the ordered implementation and acceptance tasks from the newcomer review,
see the [beta readiness follow-up plan](superpowers/plans/2026-10-30-beta-readiness-follow-up.md).
That plan separates the proposed VM preview from later desktop and hardware work;
the checkboxes below remain the release decision record.

Use the [candidate acceptance procedure](candidate-acceptance.md) to collect
evidence for the exact candidate. A local test pass does not complete these gates.

- [ ] Accept a fresh generated install through first boot, first-boot setup,
  encrypted reboot and graphical login using a different username.
- [ ] Verify Walker apps, calculator, URL search, normal/private browser launch,
  package update, provisioning repeatability and recovery.
- [ ] Record ISO hash, Archinstall version, tested source commit, disk geometry,
  successful checks and known failures. Do not publish credential exports.
- [x] Select MIT for original Hexen code and add the top-level license.
- [ ] Complete the third-party asset inventory and preserve all upstream notices.
- [ ] Review tracked/untracked files for credentials, VM disks and private data.
- [ ] Confirm anonymous access to the final candidate source archive. The
  repository is public and baseline commit download passed on 2026-11-02; see
  the [preflight record](rehearsal-preflight-2026-11-02.md). Repeat for the final
  candidate; baseline access does not include uncommitted changes.
- [ ] Commit reviewed source changes and test that exact commit. A dirty working
  tree does not establish acceptance for a GitHub checkout.
- [ ] Give the installed checkout a local branch at the tested tag with a
  configured upstream for reviewed source updates. A detached tag checkout
  skips the source-update stage; document the exact commands in release notes.
- [ ] Create a beta tag pointing to the accepted commit, then name its full commit
  in release notes for both quickstart stages. Publish limitations and recovery
  instructions. Do not imply hardware or work-account acceptance.
- [ ] Have a second person follow the quickstart without private VM notes.
- [ ] If publishing downloadable artifacts later, include hashes and build
  provenance. A custom ISO remains separate follow-up work.
