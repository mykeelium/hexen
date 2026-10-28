"""Run monitor-menu dispatch without opening a real terminal or changing displays."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

HELPER = Path(__file__).resolve().parents[1] / 'config/bin/hexen-desktop'


class MonitorHelperTest(unittest.TestCase):
    def test_hyprmon_uses_machine_state_and_preserves_existing_config(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            home = root / 'home'
            config = home / '.config/hexen'
            config.mkdir(parents=True)
            state = root / 'custom state'
            (config / 'state-home').write_text(str(state) + '\n')
            binary = root / 'bin'
            binary.mkdir()
            for name, text in {
                'hyprmon': '#!/bin/sh\nprintf "%s" "$HYPRLAND_CONFIG" > "$MONITOR_TEST_RESULT"\n',
                'ghostty': '#!/bin/sh\n[ "$1" = -e ] && shift\nexec "$@"\n',
            }.items():
                path = binary / name
                path.write_text(text)
                path.chmod(0o755)
            result_file = root / 'result'
            env = {**os.environ, 'HOME': str(home), 'PATH': f'{binary}:/usr/bin:/bin',
                   'MONITOR_TEST_RESULT': str(result_file)}
            first = subprocess.run([str(HELPER), 'monitors'], env=env, capture_output=True, timeout=4)
            self.assertEqual(first.returncode, 0, first.stderr)
            target = state / 'hexen/displays/hyprland.lua'
            self.assertEqual(result_file.read_text(), str(target))
            self.assertTrue(target.is_file())
            target.write_text('-- existing machine config\n')
            second = subprocess.run([str(HELPER), 'monitors'], env=env, capture_output=True, timeout=4)
            self.assertEqual(second.returncode, 0, second.stderr)
            self.assertEqual(target.read_text(), '-- existing machine config\n')


if __name__ == '__main__': unittest.main()
