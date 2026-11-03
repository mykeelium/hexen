"""Run hardware configuration tasks only inside a disposable filesystem."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('ansible-playbook'), 'requires ansible-playbook for hardware task integration')
class HardwareAnsibleTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.home = self.root / 'home'
        (self.home / '.config/hexen').mkdir(parents=True)
        self.etc = self.root / 'etc'
        self.etc.mkdir()

    def run_tasks(self, profile, tasks='hardware'):
        play = self.root / 'play.json'
        play.write_text(json.dumps([{'hosts': 'localhost', 'gather_facts': False, 'become': False,
            'environment': {'PATH': str(self.root / 'bin') + ':' + os.environ['PATH']},
            'vars': {'ansible_python_interpreter': sys.executable, 'desktop_hardware_profile': profile, '_desktop_home': str(self.home),
                     '_desktop_uid': os.getuid(), '_desktop_gid': os.getgid(),
                     '_desktop_hardware_etc': str(self.etc),
                     '_desktop_hardware_system_owner': str(os.getuid()),
                     '_desktop_hardware_system_group': str(os.getgid())},
            'tasks': [{'ansible.builtin.include_role': {'name': 'desktop', 'tasks_from': tasks}}]}]))
        config = self.root / 'ansible.cfg'
        config.write_text('[defaults]\nroles_path = ' + str(ROOT / 'ansible/roles') + '\n')
        return subprocess.run(['ansible-playbook', '-i', 'localhost,', '-c', 'local', str(play)],
            env={**os.environ, 'ANSIBLE_CONFIG': str(config), 'ANSIBLE_HOME': str(self.root / 'ansible-home'),
                 'ANSIBLE_LOCAL_TEMP': str(self.root / 'ansible-local'), 'ANSIBLE_REMOTE_TEMP': str(self.root / 'ansible-remote'), 'ANSIBLE_NOCOLOR': '1'},
            capture_output=True, text=True, timeout=45)

    def test_xps_configuration_is_stable_and_keeps_unrelated_settings(self):
        uwsm = self.home / '.config/uwsm'
        uwsm.mkdir()
        existing = uwsm / 'env-hyprland'
        existing.write_text('export CUSTOM_SETTING=preserve\n')
        first = self.run_tasks('xps-14-9440')
        self.assertEqual(first.returncode, 0, first.stdout + first.stderr)
        self.assertEqual(existing.read_text(), 'export CUSTOM_SETTING=preserve\n')
        self.assertEqual((self.home / '.config/hexen/hardware-profile').read_text(), 'xps-14-9440\n')
        rules = (self.etc / 'udev/rules.d/61-hexen-xps-gpu.rules').read_text()
        self.assertIn('0x7d55', rules)
        self.assertIn('0x28a1', rules)
        fragment = (uwsm / 'env-hyprland.d/10-hexen-hardware.sh').read_text()
        self.assertIn('AQ_DRM_DEVICES=/dev/dri/hexen-intel:/dev/dri/hexen-nvidia', fragment)
        second = self.run_tasks('xps-14-9440')
        self.assertEqual(second.returncode, 0, second.stdout + second.stderr)
        self.assertRegex(second.stdout, r'changed=0\s')

    def test_failed_initramfs_rebuild_is_retried_before_recording_success(self):
        configured = self.run_tasks('xps-14-9440')
        self.assertEqual(configured.returncode, 0, configured.stdout + configured.stderr)
        bindir = self.root / 'bin'
        bindir.mkdir()
        log = self.root / 'rebuilds'
        first = self.root / 'failed-once'
        for name, body in {
            'pacman': 'printf "linux 7.2.14\\nnvidia-open 615.78.08\\nnvidia-utils 615.78.08\\n"',
            'mkinitcpio': f'echo rebuild >> "{log}"; if [ ! -e "{first}" ]; then touch "{first}"; exit 1; fi',
        }.items():
            path = bindir / name
            path.write_text('#!/bin/sh\n' + body + '\n')
            path.chmod(0o755)
        stamp = self.etc / 'modprobe.d/hexen-xps-initramfs.signature'
        failed = self.run_tasks('xps-14-9440', 'hardware-initramfs')
        self.assertNotEqual(failed.returncode, 0)
        self.assertFalse(stamp.exists())
        retry = self.run_tasks('xps-14-9440', 'hardware-initramfs')
        self.assertEqual(retry.returncode, 0, retry.stdout + retry.stderr)
        self.assertTrue(stamp.exists())
        again = self.run_tasks('xps-14-9440', 'hardware-initramfs')
        self.assertEqual(again.returncode, 0, again.stdout + again.stderr)
        self.assertRegex(again.stdout, r'changed=0\s')
        self.assertEqual(log.read_text().splitlines(), ['rebuild', 'rebuild'])

    def test_generic_does_not_create_xps_configuration(self):
        result = self.run_tasks('generic')
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((self.home / '.config/uwsm').exists())
        self.assertFalse((self.etc / 'modprobe.d').exists())

    def test_symlinked_uwsm_directory_is_refused_before_profile_write(self):
        outside = self.root / 'other-config'
        outside.mkdir()
        (self.home / '.config/uwsm').symlink_to(outside, target_is_directory=True)
        result = self.run_tasks('xps-14-9440')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Hardware preflight', result.stdout)
        self.assertFalse((self.home / '.config/hexen/hardware-profile').exists())
        self.assertEqual(list(outside.iterdir()), [])

    def test_unmanaged_environment_fragment_is_preserved(self):
        target = self.home / '.config/uwsm/env-hyprland.d/10-hexen-hardware.sh'
        target.parent.mkdir(parents=True)
        target.write_text('do not replace this\n')
        result = self.run_tasks('xps-14-9440')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Hardware preflight', result.stdout)
        self.assertEqual(target.read_text(), 'do not replace this\n')


if __name__ == '__main__':
    unittest.main()
