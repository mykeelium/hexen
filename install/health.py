#!/usr/bin/env python3
"""Read-only first-boot checks; does not certify hardware or recovery readiness."""
import shutil
import subprocess
from pathlib import Path


def check_tools(find=shutil.which, launcher='walker'):
    launcher_tools = {'walker': ('walker', 'elephant'), 'fuzzel': ('fuzzel',)}
    if launcher not in launcher_tools:
        return [f'Invalid launcher setting: {launcher}']
    issues = [f'{name} missing: rerun ./install/first-boot.sh' for name in (*launcher_tools[launcher], 'Hyprland', 'nvim') if not find(name)]
    if not any(find(name) for name in ('zen-browser', 'firefox')):
        issues.append('Browser missing: install Firefox or follow the reviewed Zen procedure.')
    return issues


def main():
    launcher_file = Path.home() / '.config/hexen/launcher'
    try:
        launcher = launcher_file.read_text().strip() if launcher_file.exists() else 'walker'
    except OSError as error:
        print(f'Setup needs attention: cannot read launcher setting: {error}')
        return 1
    issues = check_tools(launcher=launcher)
    for service in ('NetworkManager', 'firewalld'):
        if subprocess.run(['systemctl', 'is-active', '--quiet', service]).returncode:
            issues.append(f'{service} inactive: inspect systemctl status {service}')
    if subprocess.run(['systemctl', 'is-enabled', '--quiet', 'sddm']).returncode:
        issues.append('sddm disabled: inspect systemctl status sddm before reboot.')
    if issues:
        print('Setup needs attention:\n' + '\n'.join('- ' + issue for issue in issues))
        return 1
    gui_active = subprocess.run(['systemctl', 'is-active', '--quiet', 'sddm']).returncode == 0
    next_step = (f'Graphical login is active. Check {launcher} and browser shortcuts in your desktop.' if gui_active
                 else 'Next: reboot, unlock the disk, and sign in through the graphical login.')
    print('Basic tools, browser and required services are present.\n' + next_step + '\nHardware, account access, updates and recovery still require acceptance checks.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
