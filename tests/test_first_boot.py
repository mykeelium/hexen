import unittest
from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]

class FirstBootTests(unittest.TestCase):
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
