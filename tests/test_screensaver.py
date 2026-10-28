"""Run the controller against disposable compositor/terminal boundaries."""
import json
import os
import pty
from pathlib import Path
import signal
import socket
import subprocess
import tempfile
import termios
import time
import unittest

HELPER = Path(__file__).resolve().parents[1] / 'config/bin/hexen-screensaver'


class ScreensaverTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.runtime = self.root / 'runtime'
        self.runtime.mkdir(mode=0o700)
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        self.log = self.root / 'terminals'
        self.pointer = self.root / 'pointer'
        self.pointer.write_text('{"x":20,"y":30}')
        self.locked = self.root / 'locked'
        self.make('hyprctl', '''#!/usr/bin/python
import json,os,sys
from pathlib import Path
if 'monitors' in sys.argv: print('[{"id":0,"name":"Virtual-1","focused":true},{"id":1,"name":"Virtual-2","focused":false}]')
elif 'cursorpos' in sys.argv:
 Path(os.environ['READY']).touch()
 print(Path(os.environ['POINTER']).read_text())
elif 'clients' in sys.argv:
 p=Path(os.environ['TERMINALS'])
 print(json.dumps([{'pid':json.loads(line)['pid'],'monitor':0} for line in p.read_text().splitlines()]) if p.exists() else '[]')
else:
 Path(os.environ['DISPATCHES']).write_text(' '.join(sys.argv[1:]))
 print('ok')
''')
        self.make('pgrep', '#!/bin/sh\n[ -f "$LOCKED" ]\n')
        self.make('loginctl', '#!/bin/sh\n[ "$1" = lock-session ] && touch "$LOCK_REQUEST"\n[ -f "$LOCKED" ] && echo yes || echo no\n')
        self.make('uv', '#!/bin/sh\nexit 0\n')
        self.make('ghostty', '''#!/usr/bin/python
import json,os,sys,time
with open(os.environ['TERMINALS'],'a') as stream: stream.write(json.dumps({'pid':os.getpid(),'argv':sys.argv})+'\\n')
time.sleep(60)
''')
        self.env = {**os.environ, 'PATH': f'{self.bin}:/usr/bin:/bin',
                    'XDG_RUNTIME_DIR': str(self.runtime), 'HYPRLAND_INSTANCE_SIGNATURE': 'test',
                    'HOME': str(self.root), 'TERMINALS': str(self.log), 'LOCK_REQUEST': str(self.root / 'lock-request'),
                    'DISPATCHES': str(self.root / 'dispatches'), 'POINTER': str(self.pointer), 'LOCKED': str(self.locked), 'READY': str(self.root / 'ready')}
        wheel = self.root / '.local/share/hexen/screensaver/terminaltexteffects-0.15.0-py3-none-any.whl'
        wheel.parent.mkdir(parents=True)
        wheel.touch()
        self.processes = []

    def make(self, name, text):
        path = self.bin / name
        path.write_text(text)
        path.chmod(0o755)

    def start(self):
        child = subprocess.Popen(['/usr/bin/python', str(HELPER), 'start'], env=self.env,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.processes.append(child)
        return child

    def wait_for(self, condition):
        deadline = time.monotonic() + 4
        while time.monotonic() < deadline:
            if condition(): return
            time.sleep(.03)
        self.fail('Timed out waiting for screensaver state')

    def terminals(self):
        return [json.loads(line) for line in self.log.read_text().splitlines()] if self.log.exists() else []

    def stop(self):
        return subprocess.run(['/usr/bin/python', str(HELPER), 'stop'], env=self.env,
                              capture_output=True, timeout=5)

    def tearDown(self):
        if HELPER.exists(): self.stop()
        for process in self.processes:
            if process.poll() is None: process.terminate()
            process.communicate(timeout=5)
        self.temporary.cleanup()

    def test_start_requires_an_installed_helper(self):
        self.assertTrue(HELPER.exists(), 'screensaver helper is missing')

    def test_duplicate_start_creates_one_terminal_per_monitor(self):
        first = self.start()
        self.wait_for(lambda: len(self.terminals()) == 2)
        duplicate = self.start()
        self.assertEqual(duplicate.wait(timeout=4), 0)
        self.assertIsNone(first.poll())
        self.assertEqual(len(self.terminals()), 2)
        self.assertEqual(self.stop().returncode, 0)
        self.assertEqual(first.wait(timeout=4), 0)

    def test_stop_terminates_owned_terminals_and_preserves_unrelated_process(self):
        unrelated = subprocess.Popen(['sleep', '60'])
        self.processes.append(unrelated)
        controller = self.start()
        self.wait_for(lambda: len(self.terminals()) == 2)
        pids = [item['pid'] for item in self.terminals()]
        self.assertEqual(self.stop().returncode, 0)
        self.assertEqual(controller.wait(timeout=4), 0)
        for pid in pids:
            with self.assertRaises(ProcessLookupError): os.kill(pid, 0)
        self.assertIsNone(unrelated.poll())

    def test_pointer_activity_dismisses_all_terminals(self):
        controller = self.start()
        self.wait_for(lambda: len(self.terminals()) == 2)
        self.wait_for(lambda: (self.root / 'ready').exists())
        time.sleep(.05)
        for x in range(21, 31):
            self.pointer.write_text(json.dumps({'x':x,'y':30}))
            time.sleep(.1)
            if controller.poll() is not None: break
        self.assertEqual(controller.wait(timeout=4), 0)

    def test_locked_session_never_opens_a_terminal(self):
        self.locked.touch()
        controller = self.start()
        self.assertEqual(controller.wait(timeout=4), 0)
        self.assertEqual(self.terminals(), [])

    def test_terminal_failure_closes_the_other_terminal(self):
        controller = self.start()
        self.wait_for(lambda: len(self.terminals()) == 2)
        os.kill(self.terminals()[0]['pid'], signal.SIGTERM)
        self.assertEqual(controller.wait(timeout=4), 0)
        with self.assertRaises(ProcessLookupError): os.kill(self.terminals()[1]['pid'], 0)

    def test_mouse_reports_and_input_dismissal_reap_the_animation(self):
        # A sleeping animation stands in for the external renderer; the real
        # helper must consume input and reap it through its PTY lifecycle.
        self.make('uv', '#!/usr/bin/python\nimport os,time\nfrom pathlib import Path\nPath(os.environ["ANIMATION_PID"]).write_text(str(os.getpid()))\ntime.sleep(60)\n')
        animation = self.root / 'animation'
        self.assertEqual(self.stop().returncode, 0)
        (next(self.runtime.glob('hexen-saver-*')) / 'ready-test-generation').touch()
        master, slave = pty.openpty()
        renderer = subprocess.Popen(['/usr/bin/python', str(HELPER), '_render', '--token', 'test-generation'],
            env={**self.env, 'ANIMATION_PID': str(animation)}, stdin=slave,
            stdout=slave, stderr=slave)
        self.processes.append(renderer)
        try:
            self.wait_for(animation.exists)
            pid = int(animation.read_text())
            self.assertTrue(termios.tcgetattr(slave)[1] & termios.OPOST, 'animation requires normal terminal newline output')
            output = os.read(master, 4096)
            self.assertIn(b'\x1b[?1003h', output, 'renderer must request mouse motion/click reports')
            self.assertIn(b'\x1b[?1006h', output, 'renderer must request SGR mouse reports')
            os.write(master, b'q')
            self.assertEqual(renderer.wait(timeout=4), 0)
            with self.assertRaises(ProcessLookupError): os.kill(pid, 0)
        finally:
            os.close(master)
            os.close(slave)

    def test_fixed_position_mouse_click_reaps_the_animation(self):
        # A sleeping animation stands in for the external renderer; the real
        # helper must consume input and reap it through its PTY lifecycle.
        self.make('uv', '#!/usr/bin/python\nimport os,time\nfrom pathlib import Path\nPath(os.environ["ANIMATION_PID"]).write_text(str(os.getpid()))\ntime.sleep(60)\n')
        animation = self.root / 'animation'
        self.assertEqual(self.stop().returncode, 0)
        (next(self.runtime.glob('hexen-saver-*')) / 'ready-test-generation').touch()
        master, slave = pty.openpty()
        renderer = subprocess.Popen(['/usr/bin/python', str(HELPER), '_render', '--token', 'test-generation'],
            env={**self.env, 'ANIMATION_PID': str(animation)}, stdin=slave,
            stdout=slave, stderr=slave)
        self.processes.append(renderer)
        try:
            self.wait_for(animation.exists)
            pid = int(animation.read_text())
            self.assertTrue(termios.tcgetattr(slave)[1] & termios.OPOST, 'animation requires normal terminal newline output')
            output = os.read(master, 4096)
            self.assertIn(b'\x1b[?1003h', output, 'renderer must request mouse motion/click reports')
            self.assertIn(b'\x1b[?1006h', output, 'renderer must request SGR mouse reports')
            os.write(master, b'\x1b[<0;20;10M')
            self.assertEqual(renderer.wait(timeout=4), 0)
            with self.assertRaises(ProcessLookupError): os.kill(pid, 0)
        finally:
            os.close(master)
            os.close(slave)

    def test_lock_appearing_while_running_closes_the_saver(self):
        controller = self.start()
        self.wait_for(lambda: len(self.terminals()) == 2)
        self.locked.touch()
        self.assertEqual(controller.wait(timeout=4), 0)

    def test_missing_wheel_opens_no_terminal(self):
        next(self.root.glob('.local/share/hexen/screensaver/*.whl')).unlink()
        controller = self.start()
        self.assertEqual(controller.wait(timeout=4), 1)
        self.assertEqual(self.terminals(), [])

    def test_nonprivate_runtime_directory_is_rejected(self):
        self.runtime.chmod(0o755)
        controller = self.start()
        self.assertEqual(controller.wait(timeout=4), 1)
        self.assertEqual(self.terminals(), [])

    def test_idle_mode_has_a_lock_deadline_even_without_new_idle_notifications(self):
        launcher = "import runpy,sys,time; clock=time.monotonic; time.monotonic=lambda:clock()*100; sys.argv=[sys.argv[1],'start','--idle']; runpy.run_path(sys.argv[0],run_name='__main__')"
        controller = subprocess.Popen(['/usr/bin/python', '-c', launcher, str(HELPER)],
            env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.processes.append(controller)
        self.assertEqual(controller.wait(timeout=4), 0)
        self.assertTrue((self.root / 'lock-request').exists())

    def test_old_renderer_message_cannot_stop_current_instance(self):
        controller = self.start()
        self.wait_for(lambda: len(self.terminals()) == 2)
        address = next(self.runtime.glob('hexen-saver-*/control'))
        with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as client:
            client.sendto(b'old-renderer-generation', str(address))
        time.sleep(.4)
        self.assertIsNone(controller.poll())

    def test_stop_is_responsive_while_a_terminal_is_mapping(self):
        self.make('hyprctl', (self.bin / 'hyprctl').read_text().replace("elif 'clients' in sys.argv:", "elif 'clients' in sys.argv: print('[]')\nelif 'unused' in sys.argv:"))
        controller = self.start()
        self.wait_for(lambda: len(self.terminals()) == 1)
        self.assertEqual(self.stop().returncode, 0)
        self.assertEqual(controller.wait(timeout=2), 0)
        self.assertEqual(len(self.terminals()), 1)

    def test_monitor_placement_does_not_warp_focus_and_reset_idle(self):
        self.make('hyprctl', (self.bin / 'hyprctl').read_text().replace("else: print('ok')", "elif any('hl.dsp.focus' in arg for arg in sys.argv): sys.exit(1)\nelse: print('ok')"))
        controller = self.start()
        self.wait_for(lambda: len(self.terminals()) == 2)
        self.assertIsNone(controller.poll())
        self.assertEqual(self.stop().returncode, 0)
        self.assertEqual(controller.wait(timeout=4), 0)

    def test_idle_action_locks_an_unlocked_session(self):
        result = subprocess.run(['/usr/bin/python', str(HELPER), 'idle-action'],
            env=self.env, capture_output=True, timeout=4)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.root / 'lock-request').exists())
        self.assertFalse((self.root / 'dispatches').exists())

    def test_idle_action_powers_off_an_already_locked_session(self):
        self.locked.touch()
        result = subprocess.run(['/usr/bin/python', str(HELPER), 'idle-action'],
            env=self.env, capture_output=True, timeout=4)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((self.root / 'lock-request').exists())
        self.assertIn('hl.dsp.dpms({action="off"})', (self.root / 'dispatches').read_text())

    def test_idle_terminal_crash_locks_instead_of_extending_the_lock_deadline(self):
        controller = subprocess.Popen(['/usr/bin/python', str(HELPER), 'start', '--idle'],
            env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.processes.append(controller)
        self.wait_for(lambda: len(self.terminals()) == 2)
        os.kill(self.terminals()[0]['pid'], signal.SIGKILL)
        self.assertEqual(controller.wait(timeout=4), 0)
        self.assertTrue((self.root / 'lock-request').exists())

    def test_idle_animation_failure_locks_instead_of_treating_failure_as_activity(self):
        controller = subprocess.Popen(['/usr/bin/python', str(HELPER), 'start', '--idle'],
            env=self.env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.processes.append(controller)
        self.wait_for(lambda: len(self.terminals()) == 2)
        argv = self.terminals()[0]['argv']
        token = argv[argv.index('--token') + 1]
        with socket.socket(socket.AF_UNIX, socket.SOCK_DGRAM) as client:
            client.sendto(b'failed:' + token.encode(), str(next(self.runtime.glob('hexen-saver-*/control'))))
        self.assertEqual(controller.wait(timeout=3), 0)
        self.assertTrue((self.root / 'lock-request').exists())

    def test_stop_without_running_instance_succeeds(self):
        self.assertTrue(HELPER.exists(), 'screensaver helper is missing')
        self.assertEqual(self.stop().returncode, 0)


if __name__ == '__main__': unittest.main()
