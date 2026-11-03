import unittest
from pathlib import Path
import importlib.util
import os
import shutil
import subprocess
import shlex
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]

class FirstBootTests(unittest.TestCase):
    def test_invalid_arguments_are_rejected_before_setup(self):
        for arguments in (['--unknown'], ['--vm', '--unknown'], ['--vm', '--vm'],
                          ['--help', '--vm'], ['--vm', '--launcher', 'fuzzel']):
            with self.subTest(arguments=arguments):
                result = subprocess.run(
                    ['bash', str(ROOT / 'install/first-boot.sh'), *arguments],
                    input='', text=True, capture_output=True, timeout=5)
                self.assertEqual(result.returncode, 2, result.stdout + result.stderr)
                self.assertIn('Usage:', result.stderr)
                self.assertNotIn('Install prerequisites', result.stdout)

    def run_completion(self, *, gui_active, health_ok=True):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            install = root / 'install'
            install.mkdir()
            for name in ('first-boot.sh', 'health.py', 'hardware-profile.sh'):
                shutil.copy(ROOT / 'install' / name, install / name)
            provision = install / 'provision.sh'
            provision.write_text('#!/bin/sh\nexit 0\n')
            provision.chmod(0o755)
            bindir = root / 'bin'
            bindir.mkdir()
            # Keep the wrapper and health report real; isolate package and service operations.
            for name in ('sudo', 'fuzzel', 'Hyprland', 'nvim', 'firefox'):
                command = bindir / name
                command.write_text('#!/bin/sh\nexit 0\n')
                command.chmod(0o755)
            (bindir / 'python3').symlink_to(sys.executable)
            systemctl = bindir / 'systemctl'
            systemctl.write_text(
                '#!/bin/sh\n'
                'case "$*" in\n'
                '  "is-active --quiet sddm") exit "$HEXEN_TEST_GUI_STATUS" ;;\n'
                '  "is-active --quiet NetworkManager") exit "$HEXEN_TEST_HEALTH_STATUS" ;;\n'
                '  "is-active --quiet firewalld"|"is-enabled --quiet sddm") exit 0 ;;\n'
                '  *) exit 99 ;;\n'
                'esac\n')
            systemctl.chmod(0o755)
            home = root / 'home'
            launcher = home / '.config/hexen/launcher'
            launcher.parent.mkdir(parents=True)
            launcher.write_text('fuzzel\n')
            return subprocess.run(
                ['script', '-q', '-e', '-c', f'bash {shlex.quote(str(install / "first-boot.sh"))}', '/dev/null'],
                input='fuzzel\ny\n', text=True, capture_output=True, timeout=10,
                env={**os.environ, 'HOME': str(home), 'PATH': f'{bindir}:/usr/bin:/bin',
                     'HEXEN_TEST_GUI_STATUS': '0' if gui_active else '3',
                     'HEXEN_TEST_HEALTH_STATUS': '0' if health_ok else '3'})

    @unittest.skipUnless(Path('/etc/arch-release').exists() and os.geteuid() != 0 and shutil.which('script'), 'requires a regular Arch account and script')
    def test_completed_first_boot_with_active_gui_does_not_request_reboot(self):
        result = self.run_completion(gui_active=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Setup completed', result.stdout)
        self.assertIn('Graphical login is active', result.stdout)
        self.assertNotIn('reboot', result.stdout.lower())

    @unittest.skipUnless(Path('/etc/arch-release').exists() and os.geteuid() != 0 and shutil.which('script'), 'requires a regular Arch account and script')
    def test_completed_first_boot_without_gui_requests_reboot_once(self):
        result = self.run_completion(gui_active=False)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Setup completed', result.stdout)
        self.assertIn('Next: reboot, unlock the disk', result.stdout)
        self.assertEqual(result.stdout.lower().count('reboot'), 1)

    @unittest.skipUnless(Path('/etc/arch-release').exists() and os.geteuid() != 0 and shutil.which('script'), 'requires a regular Arch account and script')
    def test_failed_health_check_never_reports_setup_complete(self):
        result = self.run_completion(gui_active=True, health_ok=False)
        self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('NetworkManager inactive', result.stdout)
        self.assertNotIn('Setup completed', result.stdout)

    @unittest.skipUnless(Path('/etc/arch-release').exists() and os.geteuid() != 0 and shutil.which('script'), 'requires a regular Arch account and script')
    def test_fuzzel_first_boot_skips_walker_and_forwards_choice(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            install = root / 'install'
            install.mkdir()
            shutil.copy(ROOT / 'install/first-boot.sh', install / 'first-boot.sh')
            shutil.copy(ROOT / 'install/hardware-profile.sh', install / 'hardware-profile.sh')
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

    @unittest.skipUnless(Path('/etc/arch-release').exists() and os.geteuid() != 0 and shutil.which('script'), 'requires a regular Arch account and script')
    def test_xps_first_boot_checks_hardware_before_packages_and_forwards_selection(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            install = root / 'install'
            install.mkdir()
            for name in ('first-boot.sh', 'hardware-profile.sh'):
                shutil.copy(ROOT / 'install' / name, install / name)
            log = root / 'calls'
            bindir = root / 'bin'
            bindir.mkdir()
            bodies = {
                'sudo': 'printf "sudo %s\\n" "$*" >> "$HEXEN_TEST_LOG"',
                'python3': 'printf "python %s\\n" "$*" >> "$HEXEN_TEST_LOG"; case "$*" in *hardware.py*) [ "${HEXEN_TEST_REJECT:-0}" = 0 ] || exit 1 ;; esac; case "$*" in *--packages*) printf "linux nvidia-open nvidia-utils vulkan-intel\\n" ;; esac',
            }
            for name, body in bodies.items():
                path = bindir / name
                path.write_text('#!/bin/sh\n' + body + '\n')
                path.chmod(0o755)
            provision = install / 'provision.sh'
            provision.write_text('#!/bin/sh\nprintf "provision %s\\n" "$*" >> "$HEXEN_TEST_LOG"\n')
            provision.chmod(0o755)
            env = {**os.environ, 'HOME': str(root / 'home'), 'PATH': f'{bindir}:/usr/bin:/bin', 'HEXEN_TEST_LOG': str(log)}
            command = ['script', '-q', '-e', '-c', f'bash {install / "first-boot.sh"} --hardware xps-14-9440', '/dev/null']
            result = subprocess.run(command, input='fuzzel\ny\n', text=True, capture_output=True, env=env, timeout=10)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            calls = log.read_text().splitlines()
            self.assertIn('hardware.py --profile xps-14-9440', calls[0])
            self.assertTrue(any('sudo pacman -Syu' in line and 'nvidia-open' in line for line in calls))
            self.assertIn('provision --hardware xps-14-9440 --launcher fuzzel', calls)
            log.unlink()
            result = subprocess.run(command, input='', text=True, capture_output=True, env={**env, 'HEXEN_TEST_REJECT': '1'}, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertNotIn('sudo ', log.read_text())
            self.assertNotIn('provision ', log.read_text())

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
