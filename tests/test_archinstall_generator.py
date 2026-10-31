import importlib.util
from pathlib import Path
import unittest

MODULE = Path(__file__).resolve().parents[1] / 'install/archinstall/generate.py'

class GeneratorTests(unittest.TestCase):
    def setUp(self):
        spec = importlib.util.spec_from_file_location('generator', MODULE)
        self.g = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.g)

    def test_rejects_used_or_readonly_disk(self):
        for patch in ({'children': [{'type': 'part'}]}, {'ro': True}, {'fstype': 'btrfs'}, {'pttype': 'gpt'}, {'mountpoints': ['/mnt']}):
            disk = dict(type='disk', size=64*2**30, ro=False)
            disk.update(patch)
            self.assertFalse(self.g.eligible(disk))

    def test_invalid_answer_can_be_corrected(self):
        from unittest.mock import patch
        with patch('builtins.input', side_effect=['bad', '2']), patch('builtins.print'):
            value = self.g.ask('Disk', validator=lambda value: value == '2')
        self.assertEqual(value, '2')

    def test_modified_layout_is_refused(self):
        expected = {'partitions': [{'fs': 'btrfs', 'mount': '/'}]}
        self.g.validate_layout(expected, expected)
        with self.assertRaises(ValueError):
            self.g.validate_layout({'partitions': [{'fs': 'ext4', 'mount': '/'}]}, expected)

    def test_country_codes_are_resolved_to_installer_names(self):
        mirrors = [{'country_code': 'US', 'country': 'United States', 'protocol': 'https', 'active': True, 'completion_pct': 1, 'url': 'https://mirror.example/'}]
        name, urls = self.g.resolve_mirrors(mirrors, 'US')
        self.assertEqual(name, 'United States')
        self.assertEqual(urls, ['https://mirror.example/'])
        cfg = self.g.mirror_configuration(urls)
        self.assertEqual(cfg['mirror_regions'], {})
        self.assertEqual(cfg['custom_servers'][0]['url'], 'https://mirror.example/$repo/os/$arch')

    def test_existing_system_account_is_refused(self):
        self.assertFalse(self.g.available_username('root'))
        self.assertFalse(self.g.available_username('nobody'))
        self.assertTrue(self.g.available_username('hexen_test_unused_90210'))

    def test_geometry_and_encryption(self):
        cfg = self.g.configuration('/dev/vda', 64*2**30, 4096, 'hexen', 'UTC', 'us', 'en_US', 'US')
        layout = cfg['disk_config']
        parts = layout['device_modifications'][0]['partitions']
        self.assertIn('esp', parts[0]['flags'])
        self.assertEqual(parts[0]['size']['value'], 2**30)
        self.assertEqual(parts[1]['start']['value'], 2**30 + 2**20)
        self.assertLessEqual(parts[1]['start']['value'] + parts[1]['size']['value'], 64*2**30 - 2**20)
        self.assertEqual(layout['disk_encryption']['partitions'], [parts[1]['obj_id']])
        self.assertEqual([s['name'] for s in parts[1]['btrfs']], ['@','@home','@log','@pkg'])
        self.assertIsNone(cfg['bootloader_config']['plymouth'])
        self.assertFalse(cfg['silent'])
        self.assertNotIn('custom_commands', cfg)
        self.assertNotIn('auth_config', cfg)

    def test_unaccepted_console_layout_is_rejected(self):
        with self.assertRaisesRegex(ValueError, 'US keyboard'):
            self.g.configuration('/dev/vda', 64*2**30, 512, 'hexen', 'UTC', 'de', 'en_US', 'US')

if __name__ == '__main__':
    unittest.main()
