"""Verify Hexen's fail-closed firewalld drop-zone policy."""
from pathlib import Path
import unittest
import xml.etree.ElementTree as ET
from jinja2 import Environment, StrictUndefined
import yaml

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / 'ansible/roles/base/templates/firewalld-drop.xml.j2'


class FirewallPolicyTest(unittest.TestCase):
    def render_zone(self, sources=None):
        defaults = yaml.safe_load((ROOT / 'ansible/roles/base/defaults/main.yml').read_text())
        if sources is not None:
            defaults['base_firewall_ssh_sources'] = sources
        template = Environment(undefined=StrictUndefined).from_string(POLICY.read_text())
        return ET.fromstring(template.render(defaults))

    def test_drop_zone_is_fail_closed_without_forwarding_or_host_services(self):
        zone = self.render_zone()
        self.assertEqual(zone.tag, 'zone')
        self.assertEqual(zone.attrib.get('target'), 'DROP')
        self.assertIsNone(zone.find('forward'))
        self.assertEqual(
            {service.attrib['name'] for service in zone.findall('service')},
            {'dhcpv6-client'},
        )
        self.assertEqual(zone.findall('port'), [])
        self.assertEqual(zone.findall('rule'), [])


    def test_optional_ssh_is_limited_to_explicit_sources(self):
        zone = self.render_zone(['192.0.2.10/32', '2001:db8::1/128'])
        rules = zone.findall('rule')
        self.assertEqual(len(rules), 2)
        self.assertEqual([r.attrib['family'] for r in rules], ['ipv4', 'ipv6'])
        self.assertEqual([r.find('source').attrib['address'] for r in rules], ['192.0.2.10/32', '2001:db8::1/128'])
        for rule in rules:
            self.assertEqual(rule.find('service').attrib['name'], 'ssh')
            self.assertIsNotNone(rule.find('accept'))
        self.assertIsNone(zone.find('forward'))
        self.assertEqual(zone.findall('port'), [])

if __name__ == '__main__':
    unittest.main()
