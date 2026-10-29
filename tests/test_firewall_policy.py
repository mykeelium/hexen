"""Verify Hexen's fail-closed firewalld drop-zone policy."""
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / 'ansible/roles/base/templates/firewalld-drop.xml.j2'


class FirewallPolicyTest(unittest.TestCase):
    def test_drop_zone_is_fail_closed_without_forwarding_or_host_services(self):
        zone = ET.fromstring(POLICY.read_text())
        self.assertEqual(zone.tag, 'zone')
        self.assertEqual(zone.attrib.get('target'), 'DROP')
        self.assertIsNone(zone.find('forward'))
        self.assertEqual(
            {service.attrib['name'] for service in zone.findall('service')},
            {'dhcpv6-client'},
        )
        self.assertEqual(zone.findall('port'), [])
        self.assertEqual(zone.findall('rule'), [])


if __name__ == '__main__':
    unittest.main()
