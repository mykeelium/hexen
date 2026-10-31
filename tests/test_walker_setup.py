import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]

class WalkerSetupTests(unittest.TestCase):
    def module(self):
        spec = importlib.util.spec_from_file_location('walker_setup', ROOT/'install/manual-apps/walker/setup.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_declining_review_never_builds_or_installs(self):
        module = self.module()
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            (home/'build/hexen-walker/elephant').mkdir(parents=True)
            with patch.object(module.os, 'geteuid', return_value=1000), patch.object(module.sys.stdin, 'isatty', return_value=True), patch.object(module.Path, 'home', return_value=home), patch.object(module.subprocess, 'check_output', side_effect=['fa4ae49703d0f1a2b47d3a93f0a373fb404aff39', '']), patch.object(module, 'run') as run, patch('builtins.input', return_value='n'), patch('builtins.print'):
                with self.assertRaises(SystemExit):
                    module.main()
                self.assertEqual([call.args[0] for call in run.call_args_list], ['less', 'less'])

    def test_only_requested_package_is_selected(self):
        module = self.module()
        with patch.object(module.subprocess, 'check_output', side_effect=['elephant 2.22.1-1', 'elephant-debug 2.22.1-1']):
            self.assertEqual(module.select_archives(['main.pkg.tar.zst', 'debug.pkg.tar.zst'], 'elephant'), ['main.pkg.tar.zst'])

    def test_root_never_starts_recipe_execution(self):
        module = self.module()
        with patch.object(module.os, 'geteuid', return_value=0), patch.object(module, 'run') as run:
            with self.assertRaises(SystemExit):
                module.main()
            run.assert_not_called()

if __name__ == '__main__':
    unittest.main()
