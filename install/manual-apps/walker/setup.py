#!/usr/bin/env python3
"""Guided builds of the exact recipes recorded in sources.lock; never run as root."""
import json
import os
from pathlib import Path
import subprocess
import sys


def run(*args, **kwargs):
    return subprocess.run(args, check=True, **kwargs)


def confirm(text):
    if input(text + ' [y/N] ').lower() != 'y':
        raise SystemExit('Stopped before the next action. Rerun first-boot setup to continue.')


def select_archives(archives, package):
    selected = []
    for archive in archives:
        info = subprocess.check_output(['pacman', '-Qp', '--', archive], text=True).split()
        if info and info[0] == package:
            selected.append(archive)
    if len(selected) != 1:
        raise SystemExit(f'Expected exactly one built archive for {package}; inspect the build output.')
    return selected


def main():
    if os.geteuid() == 0 or not sys.stdin.isatty():
        raise SystemExit('Run interactively as your regular desktop user, not root.')
    lock = json.loads(Path(__file__).with_name('sources.lock').read_text())
    workspace = Path.home() / 'build/hexen-walker'
    workspace.mkdir(parents=True, exist_ok=True)
    print(f'Reviewed recipe date: {lock["reviewed_on"]}. Build location: {workspace}')
    print('Community recipes execute code as your user. Read each recipe before approving its build.')
    # Elephant first so providers can resolve their local runtime dependency.
    recipes = sorted(lock['recipes'], key=lambda r: (r['package'] != 'elephant', r['package']))
    for recipe in recipes:
        name = recipe['package']
        directory = workspace / name
        if not directory.exists():
            run('git', 'clone', '--', recipe['aur'], str(directory))
        head = subprocess.check_output(['git', '-C', str(directory), 'rev-parse', 'HEAD'], text=True).strip()
        dirty = subprocess.check_output(['git', '-C', str(directory), 'status', '--porcelain', '--untracked-files=no'], text=True)
        if dirty:
            raise SystemExit(f'Tracked files changed in {directory}; inspect them before continuing.')
        if head != recipe['commit']:
            run('git', '-C', str(directory), 'checkout', '--detach', recipe['commit'])
        print(f'\n{name}: {recipe["commit"]}', flush=True)
        for filename in ('PKGBUILD', '.SRCINFO'):
            run('less', '--', str(directory / filename))
        confirm(f'Approve source verification and build of {name}?')
        run('makepkg', '--verifysource', cwd=directory)
        run('makepkg', '--syncdeps', '--cleanbuild', '--force', cwd=directory)
        archives = subprocess.check_output(['makepkg', '--packagelist'], cwd=directory, text=True).splitlines()
        if not archives or any(not Path(a).is_file() for a in archives):
            raise SystemExit(f'Missing built archives for {name}.')
        archives = select_archives(archives, name)
        for archive in archives:
            run('pacman', '-Qip', '--', archive)
            run('pacman', '-Qlp', '--', archive)
            run('sha256sum', '--', archive)
        confirm(f'Install these exact {name} archives with sudo?')
        run('sudo', 'pacman', '-U', '--', *archives)
    print('Walker and matching Elephant providers installed. Continuing to provisioning.')


if __name__ == '__main__':
    try:
        main()
    except (OSError, subprocess.CalledProcessError, EOFError, KeyboardInterrupt) as exc:
        raise SystemExit(f'Walker setup stopped: {exc}')
