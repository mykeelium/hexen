#!/usr/bin/env python3
"""Generate a non-secret Archinstall 4.5 plan on official Arch live media."""
import argparse
import getpass
import importlib.metadata
import json
import os
import pwd
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import urllib.request
import uuid
from zoneinfo import ZoneInfo

MIB = 2**20


def available_username(value):
    try:
        pwd.getpwnam(value)
        return False
    except KeyError:
        return True


def eligible(disk):
    return (disk.get('type') == 'disk' and not disk.get('ro')
            and int(disk.get('size', 0)) >= 40*2**30
            and not disk.get('children') and not disk.get('fstype') and not disk.get('pttype')
            and not any(disk.get('mountpoints') or []))


def resolve_mirrors(mirrors, country_code):
    candidates = [m for m in mirrors if m['country_code'] == country_code and m['protocol'] == 'https' and m['active'] and m['completion_pct'] == 1]
    if not candidates:
        raise ValueError('No active HTTPS mirrors for that country.')
    candidates.sort(key=lambda item: (item.get('score') is None, item.get('score') or 0))
    return candidates[0]['country'], [m['url'] for m in candidates[:5]]


def mirror_configuration(urls):
    # Region loading ignores supplied URL lists in 4.5 and scans every mirror,
    # including HTTP. Explicit servers preserve our HTTPS-only selection.
    if not urls or any(not url.startswith('https://') or '\n' in url or '\r' in url for url in urls):
        raise ValueError('Expected active HTTPS mirror URLs.')
    return {'mirror_regions': {}, 'custom_servers': [{'url': url.rstrip('/') + '/$repo/os/$arch'} for url in urls]}


def configuration(device, size, sector, hostname, timezone, keyboard, locale, region):
    def amount(value):
        return {'unit': 'B', 'value': value, 'sector_size': {'unit': 'B', 'value': sector}}
    def partition(start, length, fs, mount, flags):
        return dict(obj_id=str(uuid.uuid4()), status='create', type='primary',
                    start=amount(start), size=amount(length), fs_type=fs,
                    mountpoint=mount, mount_options=[], flags=flags, dev_path=None, btrfs=[])
    esp = partition(MIB, 1024*MIB, 'fat32', '/boot', ['boot', 'esp'])
    start = 1025*MIB
    root = partition(start, (size-MIB-start)//MIB*MIB, 'btrfs', None, [])
    root['mount_options'] = ['compress=zstd']
    root['btrfs'] = [dict(name=n, mountpoint=m) for n, m in
                     [('@', '/'), ('@home', '/home'), ('@log', '/var/log'), ('@pkg', '/var/cache/pacman/pkg')]]
    return dict(hostname=hostname, timezone=timezone, kernels=['linux'], ntp=True,
                script='guided', silent=False, packages=['git', 'ansible'],
                locale_config=dict(kb_layout=keyboard, sys_lang=locale, sys_enc='UTF-8'),
                mirror_config=dict(mirror_regions={region: []}),
                bootloader_config=dict(bootloader='Limine', uki=False, removable=False, plymouth=None),
                network_config={'type': 'nm'}, swap=dict(enabled=True, algorithm='zstd'),
                disk_config=dict(config_type='manual_partitioning', device_modifications=[
                    dict(device=device, wipe=True, partitions=[esp, root])],
                    disk_encryption=dict(encryption_type='luks', partitions=[root['obj_id']], lvm_volumes=[])))


def disks():
    return json.loads(subprocess.check_output([
        'lsblk', '--json', '--bytes', '--paths', '-o',
        'NAME,TYPE,SIZE,MODEL,SERIAL,TRAN,RO,FSTYPE,MOUNTPOINTS,LOG-SEC,PTTYPE']))['blockdevices']


def ask(label, default='', pattern=None, validator=None):
    while True:
        value = input(f'{label}' + (f' [{default}]' if default else '') + ': ').strip() or default
        try:
            valid = validator is None or validator(value)
        except (ValueError, KeyError):
            valid = False
        if value and valid and (pattern is None or re.fullmatch(pattern, value)):
            return value
        print('Please enter a valid value.')


def secret(label):
    while True:
        password = getpass.getpass(label + ': ')
        if password and password == getpass.getpass('Confirm ' + label.lower() + ': '):
            return password
        print('Passwords must be nonempty and match.')


def validate_layout(current, expected):
    if current != expected:
        raise ValueError('Disk layout changed in Archinstall; restart Hexen setup before installing.')


def handoff(path, config, username, selected_disk):
    # 4.5's DiskEncryption.parse_arg drops encryption without an in-memory Password.
    from archinstall.lib.args import ArchConfigHandler
    from archinstall.lib.models.device import DiskEncryption
    from archinstall.lib.models.users import Password, User
    from archinstall.lib.models.authentication import AuthenticationConfiguration
    from archinstall.scripts import guided
    from archinstall import main as entry
    sys.argv = ['archinstall', '--config', str(path)]
    handler = ArchConfigHandler()
    layout = handler.config.disk_config
    if layout is None or len(layout.device_modifications) != 1:
        raise ValueError('Archinstall did not load the selected disk layout')
    subprocess.run(['loadkeys', '--', config['locale_config']['kb_layout']], check=True)
    print('Password entry uses keyboard layout: ' + config['locale_config']['kb_layout'])
    layout.disk_encryption = DiskEncryption.parse_arg(
        layout, config['disk_config']['disk_encryption'], Password(plaintext=secret('Disk encryption passphrase')))
    if layout.disk_encryption is None:
        raise ValueError('Archinstall did not load disk encryption')
    handler.config.auth_config = AuthenticationConfiguration(
        users=[User(username, Password(plaintext=secret(f'Password for {username}')), True)])
    baseline = layout.json()
    original = guided.FilesystemHandler

    def checked_filesystem(current):
        # This runs AFTER menu edits and confirmation, immediately before disk changes.
        if not any(d == selected_disk and eligible(d) for d in disks()):
            raise ValueError('Disk state changed while reviewing; restart setup.')
        validate_layout(current.json(), baseline)
        enc = current.disk_encryption
        if not enc or not enc.encryption_password or not enc.encryption_password.plaintext:
            raise ValueError('Disk encryption passphrase missing; aborting before disk operations.')
        return original(current)
    guided.FilesystemHandler = checked_filesystem
    original_handler = entry.ArchConfigHandler
    entry.ArchConfigHandler = lambda: handler
    try:
        # Keep upstream database synchronization, online checks, and font lifecycle.
        if entry.main() != 0:
            raise ValueError('Archinstall failed; inspect its local install log.')
    finally:
        entry.ArchConfigHandler = original_handler
        guided.FilesystemHandler = original


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--install', action='store_true', help='experimental: launch Archinstall after reviewing the generated plan')
    parser.add_argument('--json', action='store_true', help='also display the full generated JSON')
    args = parser.parse_args()
    if not sys.stdin.isatty() or os.geteuid() != 0:
        raise ValueError('Run from an interactive root shell on the official Arch live ISO.')
    if not Path('/run/archiso').is_dir() or not Path('/sys/firmware/efi').is_dir() or os.uname().machine != 'x86_64':
        raise ValueError('Requires official x86_64 Arch live media booted in UEFI mode.')
    if os.path.ismount('/mnt'):
        raise ValueError('Unmount /mnt first; Archinstall needs it for installation staging.')
    version = importlib.metadata.version('archinstall')
    if version != '4.5':
        raise ValueError(f'Unsupported Archinstall {version}; this adapter targets exactly 4.5.')
    print('HEXEN setup — experimental; disposable VM rehearsal is still required.\nOnly a blank whole disk of at least 40 GiB is supported.')
    with urllib.request.urlopen('https://archlinux.org/mirrors/status/json/', timeout=20) as response:
        mirrors = json.load(response)['urls']
    available = [d for d in disks() if eligible(d)]
    if not available:
        raise ValueError('No eligible blank disks. Existing partitions and filesystems are refused.')
    for index, disk in enumerate(available, 1):
        print(f"{index}: {disk['name']} | {int(disk['size'])/2**30:.1f} GiB | {disk.get('model')} | serial {disk.get('serial')} | {disk.get('tran')}")
    index = int(ask('Choose disk number (no default)', pattern=r'[1-9][0-9]*', validator=lambda value: value.isdigit() and 1 <= int(value) <= len(available))) - 1
    if index >= len(available):
        raise ValueError('Invalid disk selection')
    disk = available[index]
    hostname = ask('Hostname', 'hexen', r'[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?')
    username = ask('Desktop username', pattern=r'[a-z_][a-z0-9_-]{0,30}', validator=available_username)
    if username == 'root':
        raise ValueError('Choose a regular account name, not root.')
    timezone = ask('Timezone', 'America/New_York', validator=lambda value: bool(ZoneInfo(value)))
    ZoneInfo(timezone)
    keyboard = ask('Console keyboard layout', 'us', r'[A-Za-z0-9][A-Za-z0-9_-]*')
    locale = ask('UTF-8 locale (without .UTF-8)', 'en_US', r'[a-z]{2,3}_[A-Z]{2}')
    region = ask('Mirror country code', 'US', r'[A-Z]{2}', validator=lambda value: any(m['country_code'] == value and m['protocol'] == 'https' and m['active'] and m['completion_pct'] == 1 for m in mirrors))
    region_name, urls = resolve_mirrors(mirrors, region)
    config = configuration(disk['name'], int(disk['size']), int(disk['log-sec']), hostname, timezone, keyboard, locale, region_name)
    config['mirror_config'] = mirror_configuration(urls)
    print(f"\nInstallation plan: {hostname} | account {username} (sudo)\nTimezone: {timezone} | keyboard: {keyboard} | locale: {locale}.UTF-8\nDisk: {disk['name']} | {int(disk['size'])/2**30:.1f} GiB | {disk.get('model')}\nLayout: 1 GiB EFI at /boot; remaining system space LUKS + Btrfs\nSubvolumes: @, @home, @log, @pkg | compression: zstd\nBoot: Limine | kernel: linux | zram: zstd | networking: NetworkManager\nDesktop: installed after reboot by Hexen first-boot setup")
    if args.json:
        print(json.dumps(config, indent=2))
    print(f"Account: {username} with sudo; root password unset.\nERASE ENTIRE DISK: {disk['name']} | {disk.get('model')} | serial {disk.get('serial')}")
    if not args.install:
        print('Preview complete. To launch experimental installation, rerun with --install on a disposable VM.')
        return
    if input(f"Type ERASE {disk['name']} to continue: ") != f"ERASE {disk['name']}":
        raise ValueError('Cancelled')
    if not any(d == disk and eligible(d) for d in disks()):
        raise ValueError('Disk identity or state changed; restart setup.')
    print('Review Disk encryption and Authentication in Archinstall. Do not save credentials. Select Install only after reviewing the entire plan.')
    with tempfile.TemporaryDirectory(prefix='hexen-install-', dir='/run') as directory:
        path = Path(directory) / 'configuration.json'
        with path.open('x') as output:
            os.chmod(path, 0o600)
            json.dump(config, output)
        handoff(path, config, username, disk)
    print('Archinstall returned; this alone does not prove installation succeeded.\nIf installed successfully, reboot, unlock LUKS, and log into your new account.\nFollow install/archinstall/README.md for boot verification, clone Hexen to a permanent location, then run ./install/first-boot.sh (add --vm in a VM). Sudo/BECOME means your account password.')


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, EOFError, KeyboardInterrupt, subprocess.CalledProcessError, importlib.metadata.PackageNotFoundError) as exc:
        sys.exit(f'Hexen setup stopped: {exc}')
