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
python3 -m unittest discover -s tests -p test_monitor_helper.py
python3 -m unittest discover -s tests -p test_theme_sync.py
bash -n install/first-boot.sh install/provision.sh install/archinstall/hexen-install.sh config/bin/hexen-desktop
git diff --check
```

These checks simulate external tools and do not install packages or partition
disks. They do not replace boot, GUI, update, recovery or hardware checks. The
GitHub workflow runs this focused subset, not the whole repository's acceptance
suite. A separate theme-sync job installs Ansible Core 2.19.15 in a temporary
virtual environment so the real theme-task integration case runs rather than
being skipped. It uses a temporary home and checkout plus a fake Matugen renderer;
it does not provision the runner's desktop or validate a real graphical session.

Preserve source pins, upstream notices and review boundaries when changing
third-party packages. Explain the problem, resulting behavior and validation
in each change. Never commit credentials, installer credential exports, private
keys, VM disks, account data or machine-local overrides. Review log excerpts
before including them in an issue.

The complete Python suite needs Python 3.11 or newer, Jinja2 and PyYAML
(supplied by Ansible), Pillow, and FontTools for glyph inspection. The glyph-art
test also expects JetBrainsMono Nerd Font at
`/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf`. Starship is needed for
the prompt test; that test skips when it is absent. The interactive wrappers
require a regular Arch account and `script`/PTY access. The theme-task integration
case skips unless `ansible-playbook` is on `PATH`; use the dedicated CI job's
environment to exercise it. Run `python3 -m unittest discover -s tests` and record
skips as well as failures. Screensaver controller tests
need permission to bind temporary local Unix sockets; a sandbox denying that
operation will fail those fixtures before exercising controller behavior.
