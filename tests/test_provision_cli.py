"""Exercise the real interactive wrapper without provisioning the test host."""
import errno
import json
import os
from pathlib import Path
import pty
import select
import signal
import sys
import tempfile
import time
import unittest


@unittest.skipUnless(Path('/etc/arch-release').exists() and os.geteuid() != 0,
                     'wrapper requires a regular account on Arch')
class ProvisionCliTest(unittest.TestCase):
    def run_wrapper(self, args, answers):
        script = Path(__file__).resolve().parents[1] / 'install/provision.sh'
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            log = root / 'commands.jsonl'
            for name in ('ansible-playbook', 'ansible-galaxy'):
                command = root / name
                command.write_text(
                    '#!' + sys.executable + '\n'
                    'import json, os, sys\n'
                    'with open(os.environ["HEXEN_CLI_TEST_LOG"], "a") as out:\n'
                    '    out.write(json.dumps(sys.argv) + "\\n")\n')
                command.chmod(0o755)
            child, terminal = pty.fork()
            if child == 0:
                os.execve('/usr/bin/bash', ['bash', str(script), *args], {
                    **os.environ, 'PATH': str(root) + ':/usr/bin:/bin',
                    'HEXEN_CLI_TEST_LOG': str(log),
                })
            output = bytearray()
            status = None
            try:
                os.write(terminal, answers.encode())
                deadline = time.monotonic() + 10
                while time.monotonic() < deadline:
                    readable, _, _ = select.select([terminal], [], [], .1)
                    if readable:
                        try:
                            chunk = os.read(terminal, 65536)
                        except OSError as error:
                            if error.errno != errno.EIO:
                                raise
                            break
                        if not chunk:
                            break
                        output.extend(chunk)
                else:
                    self.fail('interactive wrapper timed out: ' + output.decode())
                _, status = os.waitpid(child, 0)
            finally:
                os.close(terminal)
                if status is None:
                    os.kill(child, signal.SIGKILL)
                    os.waitpid(child, 0)
            calls = [json.loads(line) for line in log.read_text().splitlines()] if log.exists() else []
            return os.waitstatus_to_exitcode(status), output.decode(), calls

    def test_vm_mode_forwards_network_override_to_both_playbook_runs(self):
        code, output, calls = self.run_wrapper(['--vm'], 'y\nfuzzel\n')
        self.assertEqual(code, 0, output)
        playbooks = [args for args in calls if Path(args[0]).name == 'ansible-playbook']
        self.assertEqual(len(playbooks), 2)
        for args in playbooks:
            self.assertIn('desktop_libvirt_manage_default_network=false', args)
        self.assertIn('--syntax-check', playbooks[0])
        self.assertIn('--ask-become-pass', playbooks[1])

    def test_normal_mode_retains_workstation_network_behavior(self):
        code, output, calls = self.run_wrapper([], 'y\nfuzzel\n')
        self.assertEqual(code, 0, output)
        playbooks = [args for args in calls if Path(args[0]).name == 'ansible-playbook']
        self.assertEqual(len(playbooks), 2)
        for args in playbooks:
            self.assertNotIn('desktop_libvirt_manage_default_network=false', args)

    def test_cancel_does_not_run_ansible(self):
        code, output, calls = self.run_wrapper([], 'n\n')
        self.assertEqual(code, 0, output)
        self.assertEqual(calls, [])

    def test_invalid_launcher_does_not_run_ansible(self):
        code, output, calls = self.run_wrapper([], 'y\ninvalid\n')
        self.assertEqual(code, 2, output)
        self.assertEqual(calls, [])


if __name__ == '__main__':
    unittest.main()
