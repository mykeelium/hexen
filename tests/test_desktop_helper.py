"""Exercise menu cancellation and untrusted query text without real OS actions."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest


class SystemMenuTest(unittest.TestCase):
    def run_menu(self, choice):
        helper = Path(__file__).resolve().parents[1] / "config/bin/hexen-desktop"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
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
                env={**os.environ, "PATH": f"{root}:/usr/bin:/bin",
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
