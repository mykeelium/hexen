import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class BrowserFallbackTests(unittest.TestCase):
    def launch(self, zen, private):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'bash').symlink_to('/bin/bash')
            log = root / 'log'
            for name in ('firefox', 'zen-browser') if zen else ('firefox',):
                tool = root / name
                tool.write_text('#!/bin/sh\nprintf "%s %s" "${0##*/}" "$*" > "$BROWSER_LOG"\n')
                tool.chmod(0o755)
            subprocess.run([str(ROOT/'config/bin/hexen-desktop'), 'browser-private' if private else 'browser'],
                           env={**os.environ, 'PATH': str(root), 'BROWSER_LOG': str(log)}, check=True)
            return log.read_text()

    def test_firefox_is_available_without_zen(self):
        self.assertEqual(self.launch(False, False), 'firefox ')
        self.assertEqual(self.launch(False, True), 'firefox --private-window')

    def test_zen_remains_preferred(self):
        self.assertEqual(self.launch(True, False), 'zen-browser ')
        self.assertEqual(self.launch(True, True), 'zen-browser --private-window')
