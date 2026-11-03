#!/usr/bin/env python3
"""Read-only preflight for explicitly supported Hexen hardware profiles."""
import argparse
import json
import re
from pathlib import Path
import sys
import subprocess

PACKAGES = {'generic': [], 'xps-14-9440': ['linux', 'mesa', 'vulkan-intel', 'intel-media-driver', 'nvidia-open', 'nvidia-utils', 'nvidia-prime']}
PROFILES = tuple(PACKAGES)
XPS_GPUS = {'8086:7d55', '10de:28a1'}
SECURE_BOOT_VAR = 'SecureBoot-8be4df61-93ca-11d2-aa0d-00e098032b8c'


def validate(profile, sysfs=Path('/sys')):
    if profile not in PROFILES:
        raise ValueError('Unknown hardware profile: ' + profile)
    if profile == 'generic':
        return {'profile': profile, 'packages': PACKAGES[profile]}
    try:
        model = (sysfs / 'class/dmi/id/product_name').read_text().strip()
        if model != 'XPS 14 9440':
            raise ValueError('Hardware preflight: this profile requires Dell XPS 14 9440.')
        gpus = []
        for device in (sysfs / 'bus/pci/devices').iterdir():
            kind = (device / 'class').read_text().strip().lower()
            if kind.startswith('0x03'):
                vendor = (device / 'vendor').read_text().strip().lower().removeprefix('0x')
                identifier = (device / 'device').read_text().strip().lower().removeprefix('0x')
                gpus.append(vendor + ':' + identifier)
        if len(gpus) != 2 or set(gpus) != XPS_GPUS:
            raise ValueError('Hardware preflight: expected Intel 8086:7d55 and NVIDIA 10de:28a1 GPUs; found ' + ', '.join(sorted(gpus)))
        if not (sysfs / 'firmware/efi').is_dir():
            raise ValueError('Hardware preflight: UEFI boot is required.')
        secure = sysfs / 'firmware/efi/efivars' / SECURE_BOOT_VAR
        try:
            state = secure.read_bytes()
        except OSError as error:
            raise ValueError('Hardware preflight: cannot verify Secure Boot state; boot UEFI media with readable EFI variables.') from error
        if len(state) != 5 or state[4] != 0:
            raise ValueError('Hardware preflight: Secure Boot must be disabled for this candidate; signing support is deferred.')
        return {'profile': profile, 'model': model, 'gpus': sorted(gpus), 'secure_boot': False, 'packages': PACKAGES[profile]}
    except OSError as error:
        raise ValueError('Hardware preflight: cannot read hardware inventory: ' + str(error)) from error


def check_runtime(sysfs=Path('/sys'), devfs=Path('/dev')):
    """Verify the installed profile after reboot; never load or rebind a GPU."""
    try:
        for parameter in ('modeset', 'fbdev'):
            value = (sysfs / 'module/nvidia_drm/parameters' / parameter).read_text().strip()
            if value not in ('Y', '1'):
                raise ValueError('Hardware runtime: nvidia_drm ' + parameter + ' is not enabled.')
        for alias, expected in (('hexen-intel', '8086:7d55'), ('hexen-nvidia', '10de:28a1')):
            node = (devfs / 'dri' / alias).resolve(strict=True)
            if node.parent != (devfs / 'dri').resolve() or not re.fullmatch(r'card[0-9]+', node.name):
                raise ValueError('Hardware runtime: invalid DRM alias ' + alias)
            device = sysfs / 'class/drm' / node.name / 'device'
            actual = ':'.join((device / key).read_text().strip().lower().removeprefix('0x') for key in ('vendor', 'device'))
            if actual != expected:
                raise ValueError('Hardware runtime: DRM alias ' + alias + ' points at the wrong GPU.')
    except OSError as error:
        raise ValueError('Hardware runtime: GPU configuration is not active; reboot and inspect NVIDIA/udev state: ' + str(error)) from error


def check_installed_kernel():
    # No database refresh or package mutation: first boot performs the full Syu.
    installed = subprocess.check_output(['pacman', '-Q', 'linux'], text=True).strip().split()
    available = subprocess.check_output(['pacman', '-Sp', '--nodeps', '--print-format', '%v', 'linux'], text=True).strip().splitlines()
    if len(installed) != 2 or available != [installed[1]]:
        raise ValueError('Hardware preflight: update the complete Arch system with sudo pacman -Syu before installing the matched NVIDIA modules.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--profile', choices=PROFILES, required=True)
    parser.add_argument('--installed', action='store_true', help='also require the installed standard kernel to match the cached Arch repository')
    parser.add_argument('--packages', action='store_true', help='print the validated profile package list')
    parser.add_argument('--runtime', action='store_true', help='after reboot, verify NVIDIA DRM and GPU aliases')
    args = parser.parse_args()
    result = validate(args.profile)
    if args.installed and args.profile != 'generic':
        check_installed_kernel()
    if args.runtime and args.profile != 'generic':
        check_runtime()
        result['runtime'] = 'verified'
    print(' '.join(result['packages']) if args.packages else json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as error:
        print(str(error), file=sys.stderr)
        sys.exit(1)
