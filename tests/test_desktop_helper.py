"""Exercise menu cancellation and untrusted query text without real OS actions."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


class SystemMenuTest(unittest.TestCase):
    def test_settings_actions_launch_expected_tools(self):
        helper = Path(__file__).resolve().parents[1] / 'config/bin/hexen-desktop'
        cases = {
            'Network': ['ghostty', '-e', 'nmtui'],
            'Audio': ['pavucontrol'],
            'Bluetooth': ['ghostty', '--class=io.github.hexen.bluetui', '-e', 'bluetui'],
            'Review updates': ['ghostty', '--class=io.github.hexen.updatereview', '-e', 'hexen', 'update-monitor', 'review', '--tui'],
            'Diagnostics': ['ghostty', '-e', 'bash', '-c', 'hexen doctor 2>&1 | less'],
            'Getting started': ['ghostty', '-e', 'less', str(Path(__file__).resolve().parents[1] / 'docs/getting-started.txt')],
        }
        for choice, expected in cases.items():
            with self.subTest(choice=choice), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                home = root / 'home'
                launcher = home / '.config/hexen/launcher'
                launcher.parent.mkdir(parents=True)
                launcher.write_text('fuzzel\n')
                for name in ('fuzzel', 'ghostty', 'pavucontrol'):
                    path = root / name
                    body = 'printf "%s\\n" "$HEXEN_TEST_CHOICE"' if name == 'fuzzel' else 'printf "%s\\n" "${0##*/}" "$@" > "$HEXEN_TEST_LOG"'
                    path.write_text('#!/bin/sh\n' + body + '\n')
                    path.chmod(0o755)
                log = root / 'args'
                installed_helper = root / 'hexen-desktop'
                installed_helper.symlink_to(helper)
                result = subprocess.run([str(installed_helper), 'menu'], capture_output=True, text=True,
                    env={**os.environ, 'HOME': str(home), 'PATH': f'{root}:/usr/bin:/bin',
                         'HEXEN_TEST_CHOICE': choice, 'HEXEN_TEST_LOG': str(log)}, timeout=5)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertTrue(log.exists(), result.stdout)
                self.assertEqual(log.read_text().splitlines(), expected)

    def test_edit_actions_open_local_override(self):
        helper = Path(__file__).resolve().parents[1] / 'config/bin/hexen-desktop'
        for choice in ('Edit keybindings', 'Edit Hyprland appearance'):
            with self.subTest(choice=choice), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                home = root / 'home'
                launcher = home / '.config/hexen/launcher'
                launcher.parent.mkdir(parents=True)
                launcher.write_text('fuzzel\n')
                for name, body in {
                    'fuzzel': 'printf "%s\\n" "$HEXEN_TEST_CHOICE"',
                    'ghostty': 'printf "%s\\n" "$@" > "$HEXEN_TEST_LOG"',
                }.items():
                    path = root / name
                    path.write_text('#!/bin/sh\n' + body + '\n')
                    path.chmod(0o755)
                log = root / 'args'
                result = subprocess.run([str(helper), 'menu'], capture_output=True, text=True,
                    env={**os.environ, 'HOME': str(home), 'PATH': f'{root}:/usr/bin:/bin',
                         'HEXEN_TEST_CHOICE': choice, 'HEXEN_TEST_LOG': str(log)}, timeout=5)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(log.read_text().splitlines(), ['nvim', str(home / '.config/hypr/local.lua')])

    def run_menu(self, choice):
        helper = Path(__file__).resolve().parents[1] / "config/bin/hexen-desktop"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / 'home'
            launcher = home / '.config/hexen/launcher'
            launcher.parent.mkdir(parents=True)
            launcher.write_text('fuzzel\n')
            fuzzel = root / "fuzzel"
            fuzzel.write_text('#!/bin/sh\n[ "$HEXEN_TEST_CHOICE" = CANCEL ] && exit 1\nprintf "%s\\n" "$HEXEN_TEST_CHOICE"\n')
            fuzzel.chmod(0o755)
            for command in ("systemctl", "hyprctl", "loginctl"):
                path = root / command
                path.write_text(f'#!/bin/sh\nprintf "%s\\n" "{command} $*" >> "$HEXEN_TEST_ACTION_LOG"\n')
                path.chmod(0o755)
            log = root / "actions"
            result = subprocess.run(
                [str(helper), "system-menu"], capture_output=True, text=True,
                env={**os.environ, "HOME": str(home), "PATH": f"{root}:/usr/bin:/bin",
                     "HEXEN_TEST_CHOICE": choice, "HEXEN_TEST_ACTION_LOG": str(log)},
                timeout=5,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            return log.read_text() if log.exists() else ""

    def test_cancel_never_runs_a_system_action(self):
        self.assertEqual(self.run_menu("CANCEL"), "")

    def test_typed_shell_text_is_not_executed(self):
        self.assertEqual(self.run_menu("$(systemctl poweroff)"), "")

    def test_lock_selection_only_locks(self):
        self.assertEqual(self.run_menu("Lock"), "loginctl lock-session\n")


if __name__ == "__main__":
    unittest.main()
