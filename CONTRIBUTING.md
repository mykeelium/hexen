# Contributing to Hexen

Start with the public quickstart, known issues, and operations roadmap. The
current installer is a developer preview; changes to disk layout, encryption,
bootloader or package sources need fresh disposable-VM acceptance.

For onboarding changes, run these checks from the repository root:

```sh
python3 -m unittest discover -s tests -p test_archinstall_generator.py
python3 -m unittest discover -s tests -p test_first_boot.py
python3 -m unittest discover -s tests -p test_walker_setup.py
python3 -m unittest discover -s tests -p test_browser_fallback.py
python3 -m unittest discover -s tests -p test_desktop_helper.py
bash -n install/first-boot.sh install/provision.sh install/archinstall/hexen-install.sh config/bin/hexen-desktop
git diff --check
```

These checks simulate external tools and do not install packages or partition
disks. They do not replace boot, GUI, update, recovery or hardware checks. The
GitHub workflow runs this focused subset, not the whole repository's acceptance
suite.

Preserve source pins, upstream notices and review boundaries when changing
third-party packages. Explain the problem, resulting behavior and validation
in each change. Never commit credentials, installer credential exports, private
keys, VM disks, account data or machine-local overrides. Review log excerpts
before including them in an issue.

The complete Python suite additionally needs Jinja2 and PyYAML (supplied by
Ansible): `python3 -m unittest discover -s tests`. Screensaver controller tests
need permission to bind temporary local Unix sockets; a sandbox denying that
operation will fail those fixtures before exercising controller behavior.
