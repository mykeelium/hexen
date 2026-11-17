import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

COMMAND = Path(__file__).resolve().parents[1] / 'config/bin/repair-hexen-update'
loader = importlib.machinery.SourceFileLoader('repair', str(COMMAND))
spec = importlib.util.spec_from_loader(loader.name, loader)
repair = importlib.util.module_from_spec(spec)
loader.exec_module(repair)


class RepairTests(unittest.TestCase):
    def test_preview_preserves_files_and_apply_preserves_monitor_settings(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / 'config/hypr'
            config.mkdir(parents=True)
            main = config / 'hyprland.lua'
            baseline = b'-- tracked configuration\n'
            original = baseline + b'\n-- hyprmon: managed monitor profile include\nrequire("hyprmon")\n'
            main.write_bytes(original)
            generated = config / 'hyprmon.lua'
            generated.write_text('-- machine monitors\n')
            with patch.object(repair.subprocess, 'check_output', return_value=baseline), patch.object(repair.subprocess, 'run'), patch.object(repair.Path, 'home', return_value=root):
                repair.repair(root)
                self.assertEqual(main.read_bytes(), original)
                self.assertFalse((config / 'local.lua').exists())
                repair.repair(root, apply=True)
                self.assertEqual(main.read_bytes(), baseline)
                self.assertIn('require("hyprmon")', (config / 'local.lua').read_text())
                self.assertEqual(generated.read_text(), '-- machine monitors\n')
                self.assertIn('/config/hypr/hyprmon.lua', (root / '.git/info/exclude').read_text())

    def test_refuses_unrelated_edits(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            config = root / 'config/hypr'
            config.mkdir(parents=True)
            main = config / 'hyprland.lua'
            main.write_text('-- personal edits\n')
            with patch.object(repair.subprocess, 'check_output', return_value=b'-- baseline\n'):
                with self.assertRaises(RuntimeError):
                    repair.repair(root, apply=True)
            self.assertEqual(main.read_text(), '-- personal edits\n')
