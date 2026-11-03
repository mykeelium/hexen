"""Read-only hardware validation against a disposable sysfs tree."""
import importlib.util
from pathlib import Path
import subprocess
import os
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('hexen_hardware', Path(__file__).resolve().parents[1] / 'install/hardware.py')
hardware = importlib.util.module_from_spec(spec)
# The checker must be independently usable without distro-specific libraries.
if spec.loader and Path(spec.origin).exists():
    spec.loader.exec_module(hardware)


class HardwareTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.sys = Path(self.tmp.name)
        self.write('class/dmi/id/product_name', 'XPS 14 9440\n')
        for slot, vendor, device, kind in [('0000:00:02.0', '8086', '7d55', '030000'), ('0000:01:00.0', '10de', '28a1', '030200')]:
            for name, value in [('vendor', vendor), ('device', device), ('class', kind)]:
                self.write(f'bus/pci/devices/{slot}/{name}', '0x' + value)
        self.secure = self.sys / 'firmware/efi/efivars/SecureBoot-8be4df61-93ca-11d2-aa0d-00e098032b8c'
        self.secure.parent.mkdir(parents=True)
        self.secure.write_bytes(b'\x06\x00\x00\x00\x00')

    def write(self, name, value):
        p = self.sys / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(value)

    def test_runtime_requires_modesetting_and_aliases_for_the_correct_gpus(self):
        dev = self.sys / 'dev'
        (dev / 'dri').mkdir(parents=True)
        for index, alias, vendor, device in [(0, 'hexen-intel', '8086', '7d55'), (1, 'hexen-nvidia', '10de', '28a1')]:
            (dev / f'dri/card{index}').touch()
            (dev / 'dri' / alias).symlink_to(f'card{index}')
            self.write(f'class/drm/card{index}/device/vendor', '0x' + vendor)
            self.write(f'class/drm/card{index}/device/device', '0x' + device)
        self.write('module/nvidia_drm/parameters/modeset', 'Y')
        self.write('module/nvidia_drm/parameters/fbdev', 'Y')
        hardware.check_runtime(self.sys, dev)
        self.write('module/nvidia_drm/parameters/modeset', 'N')
        with self.assertRaisesRegex(ValueError, 'modeset'):
            hardware.check_runtime(self.sys, dev)
        self.write('module/nvidia_drm/parameters/modeset', 'Y')
        (dev / 'dri/hexen-intel').unlink()
        (dev / 'dri/hexen-intel').symlink_to('card1')
        with self.assertRaisesRegex(ValueError, 'hexen-intel'):
            hardware.check_runtime(self.sys, dev)

    def test_installed_kernel_must_match_repository_before_module_install(self):
        with patch.object(hardware.subprocess, 'check_output', side_effect=['linux 7.2.14.arch1-1\n', '7.2.14.arch1-1\n']):
            hardware.check_installed_kernel()
        with patch.object(hardware.subprocess, 'check_output', side_effect=['linux 7.2.13.arch1-1\n', '7.2.14.arch1-1\n']):
            with self.assertRaisesRegex(ValueError, 'Syu'):
                hardware.check_installed_kernel()

    def test_saved_profile_is_reused_and_cannot_be_silently_downgraded(self):
        home = self.sys / 'home'
        setting = home / '.config/hexen/hardware-profile'
        setting.parent.mkdir(parents=True)
        setting.write_text('xps-14-9440\n')
        library = Path(__file__).resolve().parents[1] / 'install/hardware-profile.sh'
        def resolve(choice, vm):
            return subprocess.run(['bash', '-c', 'set -e; source "$1"; resolve_hardware_profile "$2" "$3"; printf "%s" "$hardware_profile"', 'bash', str(library), choice, vm], env={**os.environ, 'HOME': str(home)}, capture_output=True, text=True)
        result = resolve('', 'false')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, 'xps-14-9440')
        self.assertNotEqual(resolve('generic', 'false').returncode, 0)
        self.assertNotEqual(resolve('', 'true').returncode, 0)
        setting.unlink()
        setting.symlink_to(home / 'missing')
        self.assertNotEqual(resolve('', 'false').returncode, 0)

    def test_accepts_exact_xps_inventory_without_modifying_it(self):
        before = {str(p): p.read_bytes() for p in self.sys.rglob('*') if p.is_file()}
        result = hardware.validate('xps-14-9440', self.sys)
        self.assertEqual(result['model'], 'XPS 14 9440')
        self.assertEqual(result['gpus'], ['10de:28a1', '8086:7d55'])
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.sys.rglob('*') if p.is_file()})

    def test_generic_does_not_require_xps_hardware(self):
        self.assertEqual(hardware.validate('generic', self.sys / 'absent')['profile'], 'generic')

    def test_rejects_wrong_model(self):
        self.write('class/dmi/id/product_name', 'XPS 15 9510')
        with self.assertRaisesRegex(ValueError, 'XPS 14 9440'):
            hardware.validate('xps-14-9440', self.sys)

    def test_rejects_missing_or_additional_gpu(self):
        self.write('bus/pci/devices/0000:01:00.0/device', '0x28a0')
        with self.assertRaisesRegex(ValueError, 'GPU'):
            hardware.validate('xps-14-9440', self.sys)

    def test_rejects_enabled_unknown_or_malformed_secure_boot(self):
        for contents in (b'\x06\x00\x00\x00\x01', b'', b'\0'*4+b'\x02'):
            with self.subTest(contents=contents):
                self.secure.write_bytes(contents)
                with self.assertRaisesRegex(ValueError, 'Secure Boot'):
                    hardware.validate('xps-14-9440', self.sys)
        self.secure.unlink()
        with self.assertRaisesRegex(ValueError, 'Secure Boot'):
            hardware.validate('xps-14-9440', self.sys)

    def test_rejects_bios_and_unknown_profile(self):
        self.secure.unlink()
        self.secure.parent.rmdir()
        self.secure.parent.parent.rmdir()
        with self.assertRaisesRegex(ValueError, 'UEFI'):
            hardware.validate('xps-14-9440', self.sys)
        with self.assertRaisesRegex(ValueError, 'profile'):
            hardware.validate('guessed', self.sys)


if __name__ == '__main__':
    unittest.main()
