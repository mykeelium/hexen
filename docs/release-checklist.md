# Developer preview release checklist

- [ ] Accept a fresh generated install through first boot, first-boot setup,
  encrypted reboot and graphical login using a different username.
- [ ] Verify Walker apps, calculator, URL search, normal/private browser launch,
  package update, provisioning repeatability and recovery.
- [ ] Record ISO hash, Archinstall version, tested source commit, disk geometry,
  successful checks and known failures. Do not publish credential exports.
- [x] Select MIT for original Hexen code and add the top-level license.
- [ ] Complete the third-party asset inventory and preserve all upstream notices.
- [ ] Review tracked/untracked files for credentials, VM disks and private data.
- [ ] Confirm anonymous access to the repository and source archive; the configured
  `mykeelium/hexen` repository is currently private (verified via GitHub API).
- [ ] Commit reviewed source changes and test that exact commit. A dirty working
  tree does not establish acceptance for a GitHub checkout.
- [ ] Give the installed checkout a local branch at the tested tag with a
  configured upstream for reviewed source updates. A detached tag checkout
  skips the source-update stage; document the exact commands in release notes.
- [ ] Create a beta tag pointing to the accepted commit, then use that exact tag
  in both quickstart clone stages. Publish notes with limitations and recovery
  instructions. Do not imply hardware or work-account acceptance.
- [ ] Have a second person follow the quickstart without private VM notes.
- [ ] If publishing downloadable artifacts later, include hashes and build
  provenance. A custom ISO remains separate follow-up work.
