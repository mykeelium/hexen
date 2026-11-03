"""Exercise theme regeneration without touching the host desktop or config."""
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class ThemeSyncTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='hexen-theme-sync-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.repo = self.root / 'repo'
        self.helper = self.repo / 'config/bin/hexen-theme'
        self.helper.parent.mkdir(parents=True)
        shutil.copy(ROOT / 'config/bin/hexen-theme', self.helper)
        self.themes = self.repo / 'config/themes'
        shutil.copytree(ROOT / 'config/themes', self.themes)
        self.home = self.root / 'home'
        self.home.mkdir()
        self.state = self.root / 'state'
        self.generated = self.state / 'hexen/themes'
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        (self.bin / 'python3').symlink_to(sys.executable)
        matugen = self.bin / 'matugen'
        # Only the external renderer is faked; manifest parsing, staging,
        # comparisons, activation and CLI behavior remain real.
        matugen.write_text(
            '#!' + sys.executable + '\n'
            'import os, pathlib, sys, tomllib\n'
            'if os.environ.get("HEXEN_TEST_RENDER_FAIL"): sys.exit(17)\n'
            'config = pathlib.Path(sys.argv[sys.argv.index("-c") + 1])\n'
            'data = tomllib.loads(config.read_text())\n'
            'source = pathlib.Path(sys.argv[2]).read_bytes()\n'
            'if sys.argv[1] == "image" and os.environ.get("HEXEN_TEST_FIXED_IMAGE_PALETTE"):\n'
            '    source = b"identical extracted colors"\n'
            'for template in data["templates"].values():\n'
            '    output = pathlib.Path(template["output_path"])\n'
            '    if output.name == os.environ.get("HEXEN_TEST_SKIP_OUTPUT"): continue\n'
            '    output.write_bytes(pathlib.Path(template["input_path"]).read_bytes() + source)\n')
        matugen.chmod(0o755)
        self.env = {**os.environ, 'HOME': str(self.home),
                    'XDG_STATE_HOME': str(self.state), 'PATH': str(self.bin)}
        for name in ('HYPRLAND_INSTANCE_SIGNATURE', 'HEXEN_TEST_RENDER_FAIL', 'HEXEN_TEST_SKIP_OUTPUT'):
            self.env.pop(name, None)

    def run_theme(self, *arguments, **extra_env):
        return subprocess.run([sys.executable, str(self.helper), *arguments],
                              env={**self.env, **extra_env}, text=True,
                              capture_output=True, timeout=5)

    def sync(self, *, changed, check=False):
        result = self.run_theme('sync', *(['--check'] if check else []))
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report['changed'], changed)
        return report

    def select(self, slug='gruvbox-dark'):
        result = self.run_theme('apply', slug)
        self.assertEqual(result.returncode, 0, result.stderr)
        return (self.generated / 'current').resolve(strict=True)

    def test_first_sync_initializes_default_and_repeat_is_unchanged(self):
        self.assertEqual(self.sync(changed=True)['slug'], 'tokyo-night')
        target = (self.generated / 'current').resolve(strict=True)
        self.assertEqual(self.sync(changed=False)['slug'], 'tokyo-night')
        self.assertEqual((self.generated / 'current').resolve(strict=True), target)
        self.assertEqual(len(list(self.generated.glob('tokyo-night-*'))), 1)

    def test_template_update_regenerates_selected_theme_and_retains_previous_output(self):
        old = self.select()
        template = self.themes / 'templates/waybar.css'
        template.write_text(template.read_text() + '\n/* updated template */\n')
        self.assertEqual(self.sync(changed=True)['slug'], 'gruvbox-dark')
        new = (self.generated / 'current').resolve(strict=True)
        self.assertNotEqual(new, old)
        self.assertIn('updated template', (new / 'waybar.css').read_text())
        self.assertNotIn('updated template', (old / 'waybar.css').read_text())
        self.sync(changed=False)

    def test_palette_update_regenerates_selected_theme(self):
        old = self.select()
        palette = self.themes / 'gruvbox-dark/palette.json'
        palette.write_text(palette.read_text() + '\n')
        self.sync(changed=True)
        self.assertNotEqual((self.generated / 'current').resolve(strict=True), old)

    def test_changed_wallpaper_content_regenerates_theme(self):
        self.env['HEXEN_TEST_FIXED_IMAGE_PALETTE'] = '1'
        pack = self.themes / 'wallpaper-test'
        pack.mkdir()
        (pack / 'theme.toml').write_text('name = "Wallpaper"\nmode = "dark"\n'
                                        'type = "scheme-tonal-spot"\nwallpaper = "image.png"\n')
        image = pack / 'image.png'
        image.write_bytes(b'first image fixture')
        old = self.select('wallpaper-test')
        image.write_bytes(b'second image fixture')
        self.assertEqual(self.sync(changed=True)['slug'], 'wallpaper-test')
        self.assertNotEqual((self.generated / 'current').resolve(strict=True), old)

    def test_changed_inactive_pack_does_not_regenerate_selected_theme(self):
        old = self.select()
        palette = self.themes / 'tokyo-night/palette.json'
        palette.write_text(palette.read_text() + '\n')
        self.sync(changed=False)
        self.assertEqual((self.generated / 'current').resolve(strict=True), old)

    def test_updated_renderer_output_regenerates_without_pack_changes(self):
        old = self.select()
        renderer = self.bin / 'matugen'
        renderer.write_text(renderer.read_text().replace(
            '.read_bytes() + source)', '.read_bytes() + source + b"new renderer output")'))
        self.sync(changed=True)
        self.assertNotEqual((self.generated / 'current').resolve(strict=True), old)
        self.assertIn('new renderer output', (self.generated / 'current/waybar.css').read_text())

    def test_preview_without_selection_writes_no_persistent_state(self):
        self.assertEqual(self.sync(changed=True, check=True)['slug'], 'tokyo-night')
        self.assertFalse(self.state.exists())
        self.assertFalse((self.home / '.config').exists())

    def test_preview_existing_theme_preserves_selection_and_output(self):
        old = self.select()
        before = sorted(path.name for path in self.generated.iterdir())
        self.sync(changed=False, check=True)
        template = self.themes / 'templates/hyprlock.conf'
        template.write_text(template.read_text() + '\n# changed lock colors\n')
        self.assertEqual(self.sync(changed=True, check=True)['slug'], 'gruvbox-dark')
        self.assertEqual((self.generated / 'current').resolve(strict=True), old)
        self.assertEqual(sorted(path.name for path in self.generated.iterdir()), before)
        self.assertNotIn('changed lock colors', (old / 'hyprlock.conf').read_text())

    def test_render_failure_preserves_active_theme(self):
        old = self.select()
        result = self.run_theme('sync', HEXEN_TEST_RENDER_FAIL='1')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Matugen could not render', result.stderr)
        self.assertEqual((self.generated / 'current').resolve(strict=True), old)
        self.assertFalse(any(path.name.startswith('.') for path in self.generated.iterdir()))

    def test_missing_rendered_output_preserves_active_theme(self):
        old = self.select()
        result = self.run_theme('sync', HEXEN_TEST_SKIP_OUTPUT='waybar.css')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('all expected theme fragments', result.stderr)
        self.assertEqual((self.generated / 'current').resolve(strict=True), old)

    def test_removed_selected_pack_fails_without_resetting_to_default(self):
        old = self.select()
        shutil.rmtree(self.themes / 'gruvbox-dark')
        result = self.run_theme('sync')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('unknown theme pack: gruvbox-dark', result.stderr)
        self.assertEqual((self.generated / 'current').resolve(strict=True), old)

    def test_missing_active_fragment_or_legacy_wallpaper_digest_is_repaired(self):
        for name in ('hyprpaper.conf', 'wallpaper.sha256'):
            with self.subTest(name=name):
                old = self.select()
                (old / name).unlink()
                self.sync(changed=True)
                self.assertTrue((self.generated / 'current' / name).is_file())
                self.sync(changed=False)

    def test_broken_active_selection_is_not_replaced(self):
        self.select()
        current = self.generated / 'current'
        current.unlink()
        current.symlink_to('missing-generation')
        result = self.run_theme('sync')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('active theme link is broken', result.stderr)
        self.assertEqual(os.readlink(current), 'missing-generation')

    def test_unchanged_and_preview_sync_do_not_reload_live_desktop(self):
        self.select()
        log = self.root / 'desktop-actions'
        for name in ('hyprctl', 'pkill', 'makoctl'):
            command = self.bin / name
            command.write_text(
                '#!' + sys.executable + '\n'
                'import os, pathlib, sys\n'
                'with pathlib.Path(os.environ["HEXEN_TEST_DESKTOP_LOG"]).open("a") as output:\n'
                '    output.write(pathlib.Path(sys.argv[0]).name + " " + " ".join(sys.argv[1:]) + "\\n")\n')
            command.chmod(0o755)
        live = {'HYPRLAND_INSTANCE_SIGNATURE': 'fixture', 'HEXEN_TEST_DESKTOP_LOG': str(log)}
        result = self.run_theme('sync', **live)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(json.loads(result.stdout)['changed'])
        self.assertFalse(log.exists())
        template = self.themes / 'templates/waybar.css'
        template.write_text(template.read_text() + '\n/* live update */\n')
        preview = self.run_theme('sync', '--check', **live)
        self.assertEqual(preview.returncode, 0, preview.stderr)
        self.assertTrue(json.loads(preview.stdout)['changed'])
        self.assertFalse(log.exists())
        applied = self.run_theme('sync', **live)
        self.assertEqual(applied.returncode, 0, applied.stderr)
        self.assertIn('hyprctl reload\n', log.read_text())
        self.assertIn('pkill -SIGUSR2 -x waybar\n', log.read_text())

    @unittest.skipUnless(shutil.which('ansible-playbook'), 'requires ansible-playbook for task integration')
    def test_ansible_task_previews_and_applies_selected_theme_idempotently(self):
        import pwd
        playbook = self.root / 'playbook.json'
        playbook.write_text(json.dumps([{
            'name': 'Isolated theme task integration', 'hosts': 'localhost',
            'connection': 'local', 'gather_facts': False,
            'vars': {'desktop_user': pwd.getpwuid(os.getuid()).pw_name,
                     '_desktop_home': str(self.home), 'desktop_repo_root': str(self.repo),
                     'desktop_xdg_state_home': str(self.state), 'ansible_become': False,
                     'ansible_python_interpreter': sys.executable},
            'environment': {'PATH': str(self.bin)},
            'tasks': [{'ansible.builtin.import_tasks':
                       str(ROOT / 'ansible/roles/desktop/tasks/theme.yml')}],
        }]))
        config = self.root / 'ansible.cfg'
        config.write_text('[defaults]\nretry_files_enabled=False\n')
        env = {**os.environ, 'ANSIBLE_CONFIG': str(config),
               'ANSIBLE_HOME': str(self.root / 'ansible-home'),
               'ANSIBLE_LOCAL_TEMP': str(self.root / 'ansible-local'),
               'ANSIBLE_REMOTE_TEMP': str(self.root / 'ansible-remote'),
               'ANSIBLE_NOCOLOR': '1', 'HYPRLAND_INSTANCE_SIGNATURE': ''}

        def run_task(*, check=False, changed):
            result = subprocess.run(
                [shutil.which('ansible-playbook'), '-i', 'localhost,', str(playbook),
                 *(['--check'] if check else [])],
                env=env, text=True, capture_output=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            recap = re.search(r'changed=(\d+)', result.stdout)
            self.assertIsNotNone(recap, result.stdout)
            self.assertEqual(int(recap[1]), changed, result.stdout)
            return result

        renderer = self.bin / 'matugen'
        renderer.rename(self.bin / 'matugen-disabled')
        try:
            missing = run_task(check=True, changed=1)
            self.assertIn('Theme preview is unavailable', missing.stdout)
            self.assertFalse(self.state.exists())
        finally:
            (self.bin / 'matugen-disabled').rename(renderer)
        run_task(check=True, changed=1)
        self.assertFalse(self.state.exists())
        run_task(changed=1)
        run_task(changed=0)
        old = self.select()
        template = self.themes / 'templates/waybar.css'
        template.write_text(template.read_text() + '\n/* updated via provisioning */\n')
        run_task(check=True, changed=1)
        self.assertEqual((self.generated / 'current').resolve(strict=True), old)
        run_task(changed=1)
        self.assertEqual((self.generated / 'current/slug').read_text().strip(), 'gruvbox-dark')
        self.assertIn('updated via provisioning', (self.generated / 'current/waybar.css').read_text())
        run_task(changed=0)


if __name__ == '__main__':
    unittest.main()
