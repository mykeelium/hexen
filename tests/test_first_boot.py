import unittest
from pathlib import Path
import importlib.util
import os
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]

class FirstBootTests(unittest.TestCase):
    @unittest.skipUnless(Path('/etc/arch-release').exists() and os.geteuid() != 0 and shutil.which('script'), 'requires a regular Arch account and script')
    def test_fuzzel_first_boot_skips_walker_and_forwards_choice(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            install = root / 'install'
            install.mkdir()
            shutil.copy(ROOT / 'install/first-boot.sh', install / 'first-boot.sh')
            log = root / 'calls'
            provision = install / 'provision.sh'
            provision.write_text('#!/bin/sh\nprintf "provision %s\\n" "$*" >> "$HEXEN_TEST_LOG"\nexit "${HEXEN_TEST_PROVISION_STATUS:-0}"\n')
            provision.chmod(0o755)
            bindir = root / 'bin'
            bindir.mkdir()
            for name in ('sudo', 'pacman', 'python3'):
                command = bindir / name
                command.write_text('#!/bin/sh\nprintf "%s %s\\n" "${0##*/}" "$*" >> "$HEXEN_TEST_LOG"\n')
                command.chmod(0o755)
            result = subprocess.run(['script', '-q', '-e', '-c', f'bash {install / "first-boot.sh"}', '/dev/null'], input='fuzzel\ny\n', text=True, capture_output=True, env={**os.environ, 'PATH': f'{bindir}:/usr/bin:/bin', 'HEXEN_TEST_LOG': str(log)}, timeout=10)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            calls = log.read_text()
            self.assertIn('provision --launcher fuzzel', calls)
            self.assertNotIn('walker/setup.py', calls)
            self.assertNotIn('libqalculate', calls)
            log.unlink()
            cancelled = subprocess.run(['script', '-q', '-e', '-c', f'bash {install / "first-boot.sh"}', '/dev/null'], input='fuzzel\ny\n', text=True, capture_output=True, env={**os.environ, 'PATH': f'{bindir}:/usr/bin:/bin', 'HEXEN_TEST_LOG': str(log), 'HEXEN_TEST_PROVISION_STATUS': '3'}, timeout=10)
            self.assertEqual(cancelled.returncode, 3, cancelled.stdout + cancelled.stderr)
            self.assertNotIn('Setup completed', cancelled.stdout)
            self.assertNotIn('health.py', log.read_text())

            log.unlink()
            declined = subprocess.run(['script', '-q', '-e', '-c', f'bash {install / "first-boot.sh"}', '/dev/null'], input='fuzzel\nn\n', text=True, capture_output=True, env={**os.environ, 'PATH': f'{bindir}:/usr/bin:/bin', 'HEXEN_TEST_LOG': str(log)}, timeout=10)
            self.assertEqual(declined.returncode, 3, declined.stdout + declined.stderr)
            self.assertNotIn('Setup completed', declined.stdout)
            self.assertFalse(log.exists(), 'cancelling before prerequisites must run no package commands')

            (bindir / 'pacman').write_text('#!/bin/sh\nprintf "pacman %s\\n" "$*" >> "$HEXEN_TEST_LOG"\nexit 1\n')
            (bindir / 'python3').write_text('#!/bin/sh\nprintf "python3 %s\\n" "$*" >> "$HEXEN_TEST_LOG"\nexit 7\n')
            failed = subprocess.run(['script', '-q', '-e', '-c', f'bash {install / "first-boot.sh"}', '/dev/null'], input='walker\ny\n', text=True, capture_output=True, env={**os.environ, 'PATH': f'{bindir}:/usr/bin:/bin', 'HEXEN_TEST_LOG': str(log)}, timeout=10)
            self.assertEqual(failed.returncode, 7, failed.stdout + failed.stderr)
            self.assertNotIn('Setup completed', failed.stdout)
            self.assertIn('walker/setup.py', log.read_text())
            self.assertNotIn('provision ', log.read_text())
            self.assertNotIn('health.py', log.read_text())

    def test_fuzzel_health_does_not_require_walker(self):
        spec = importlib.util.spec_from_file_location('health', ROOT / 'install/health.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        installed = {'fuzzel', 'Hyprland', 'nvim', 'firefox'}
        self.assertEqual(module.check_tools(lambda name: name if name in installed else None, 'fuzzel'), [])

    def test_preflight_reports_missing_tools(self):
        spec = importlib.util.spec_from_file_location('health', ROOT / 'install/health.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        issues = module.check_tools(lambda name: None)
        self.assertTrue(any('walker' in issue for issue in issues))
        self.assertTrue(any('browser' in issue.lower() for issue in issues))

    def test_sddm_only_needs_to_be_enabled_before_reboot(self):
        from unittest.mock import patch
        spec = importlib.util.spec_from_file_location('health', ROOT / 'install/health.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        from types import SimpleNamespace
        with patch.object(module, 'check_tools', return_value=[]), patch.object(module.subprocess, 'run', return_value=SimpleNamespace(returncode=0)) as run:
            self.assertEqual(module.main(), 0)
        self.assertIn((['systemctl', 'is-enabled', '--quiet', 'sddm'],), [call.args for call in run.call_args_list])

    def test_active_gui_does_not_request_another_reboot(self):
        from unittest.mock import patch
        from types import SimpleNamespace
        spec = importlib.util.spec_from_file_location('health', ROOT / 'install/health.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        with patch.object(module, 'check_tools', return_value=[]), patch.object(module.subprocess, 'run', return_value=SimpleNamespace(returncode=0)), patch('builtins.print') as output:
            self.assertEqual(module.main(), 0)
        messages = ' '.join(str(call.args) for call in output.call_args_list)
        self.assertNotIn('Next: reboot', messages)

if __name__ == '__main__':
    unittest.main()
