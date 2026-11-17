import importlib.machinery
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

loader = importlib.machinery.SourceFileLoader('walk', str(Path(__file__).resolve().parents[1] / 'config/bin/aur-walk'))
spec = importlib.util.spec_from_loader(loader.name, loader)
w = importlib.util.module_from_spec(spec)
loader.exec_module(w)


def git(path, *args):
    result = subprocess.run(['git', '-c', 'commit.gpgsign=false', '-c', 'core.hooksPath=/dev/null', *args], cwd=path, capture_output=True, text=True, check=True)
    return result.stdout.strip()


class Transactions(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.remote = self.root / 'upstream'
        self.remote.mkdir()
        git(self.remote, 'init', '-b', 'main')
        git(self.remote, 'config', 'user.name', 'Test')
        git(self.remote, 'config', 'user.email', 'test@example.invalid')
        (self.remote / 'PKGBUILD').write_text('pkgver=1\n')
        (self.remote / 'hook.install').write_text('echo first\n')
        git(self.remote, 'add', '.')
        git(self.remote, 'commit', '-m', 'initial')
        self.checkout = self.root / 'package'
        git(self.root, 'clone', str(self.remote), str(self.checkout))
        self.initial = git(self.checkout, 'rev-parse', 'HEAD')
        self.store = w.Store(self.root / 'state.json')
        self.package = w.Package(self.checkout, {'installed': self.initial})

    def advance(self):
        (self.remote / 'PKGBUILD').write_text('pkgver=2\n')
        (self.remote / 'hook.install').write_text('echo second\n')
        git(self.remote, 'add', '.')
        git(self.remote, 'commit', '-m', 'update')
        return git(self.remote, 'rev-parse', 'HEAD')

    def test_fetch_and_review_do_not_modify_checkout(self):
        updated = self.advance()
        self.package.fetch()
        approved, review = self.package.review()
        self.assertEqual(approved, updated)
        self.assertIn('-pkgver=1', review)
        self.assertIn('+pkgver=2', review)
        self.assertIn('echo second', review)
        self.assertEqual(git(self.checkout, 'rev-parse', 'HEAD'), self.initial)
        self.assertEqual((self.checkout / 'PKGBUILD').read_text(), 'pkgver=1\n')

    def test_exact_approved_commit_and_skipped_install_stays_pending(self):
        updated = self.advance()
        self.package.fetch()
        approved, _ = self.package.review()
        # New remote changes after review must not change the approved build.
        (self.remote / 'hook.install').write_text('echo third\n')
        git(self.remote, 'commit', '-am', 'third')
        self.package.prepare(approved)
        self.assertEqual(git(self.checkout, 'rev-parse', 'HEAD'), updated)
        self.package.refresh()
        self.assertIn('install available', self.package.status)
        _, review = self.package.review()
        self.assertIn('-pkgver=1', review)

    def test_dirty_tracked_input_is_preserved(self):
        self.advance()
        self.package.fetch()
        approved, _ = self.package.review()
        (self.checkout / 'PKGBUILD').write_text('local changes\n')
        with self.assertRaises(w.Error):
            self.package.prepare(approved)
        self.assertEqual((self.checkout / 'PKGBUILD').read_text(), 'local changes\n')
        self.assertEqual(git(self.checkout, 'rev-parse', 'HEAD'), self.initial)

    def test_diverged_checkout_is_preserved(self):
        git(self.checkout, 'config', 'user.name', 'Test')
        git(self.checkout, 'config', 'user.email', 'test@example.invalid')
        (self.checkout / 'local').write_text('local\n')
        git(self.checkout, 'add', '.')
        git(self.checkout, 'commit', '-m', 'local branch')
        self.advance()
        self.package.fetch()
        approved, _ = self.package.review()
        local = git(self.checkout, 'rev-parse', 'HEAD')
        with self.assertRaises(w.Error):
            self.package.prepare(approved)
        self.assertEqual(git(self.checkout, 'rev-parse', 'HEAD'), local)

    def test_untracked_artifacts_allowed_but_collisions_preserved(self):
        (self.checkout / 'src').mkdir()
        (self.checkout / 'src/file').write_text('build output')
        (self.checkout / 'new-input').write_text('my work')
        (self.remote / 'new-input').write_text('remote input')
        git(self.remote, 'add', '.')
        git(self.remote, 'commit', '-m', 'new input')
        self.package.fetch()
        approved, _ = self.package.review()
        with self.assertRaises(w.Error):
            self.package.prepare(approved)
        self.assertEqual((self.checkout / 'new-input').read_text(), 'my work')
        (self.checkout / 'new-input').unlink()
        self.package.prepare(approved)
        self.assertEqual((self.checkout / 'src/file').read_text(), 'build output')

    def fake_build(self, install_code=0, build_code=0):
        artifact = self.root / 'out with spaces.pkg.tar.zst'
        artifact.touch()
        calls = []
        def execute(argv, **kwargs):
            calls.append(argv)
            if argv[0] == 'sudo':
                return subprocess.CompletedProcess(argv, install_code)
            return subprocess.CompletedProcess(argv, build_code)
        metadata = subprocess.CompletedProcess([], 0, str(artifact) + '\n', '')
        return artifact, calls, execute, metadata

    def test_install_success_records_state_and_exact_artifact(self):
        approved, _ = self.package.review()
        artifact, calls, execute, metadata = self.fake_build()
        with patch.object(self.package, 'prepare'), patch.object(w.subprocess, 'run', execute), patch.object(w, 'run', return_value=metadata), patch('builtins.input', return_value='y'):
            w.build_install(self.package, approved, self.store)
        self.assertEqual(calls[-1], ['sudo', 'pacman', '-U', '--', str(artifact)])
        self.assertEqual(w.Store(self.store.path).data[str(self.checkout)]['installed'], approved)

    def test_skip_and_failed_install_never_save_state(self):
        approved, _ = self.package.review()
        _, calls, execute, metadata = self.fake_build(install_code=1)
        with patch.object(self.package, 'prepare'), patch.object(w.subprocess, 'run', execute), patch.object(w, 'run', return_value=metadata):
            with patch('builtins.input', return_value='n'):
                w.build_install(self.package, approved, self.store)
            self.assertFalse(any(c[0] == 'sudo' for c in calls))
            with patch('builtins.input', return_value='y'), self.assertRaises(w.Error):
                w.build_install(self.package, approved, self.store)
        self.assertFalse(self.store.path.exists())

    def test_failed_build_never_queries_or_installs(self):
        approved, _ = self.package.review()
        _, calls, execute, _ = self.fake_build(build_code=1)
        with patch.object(self.package, 'prepare'), patch.object(w.subprocess, 'run', execute), patch.object(w, 'run') as metadata, self.assertRaises(w.Error):
            w.build_install(self.package, approved, self.store)
        metadata.assert_not_called()
        self.assertFalse(self.store.path.exists())
        self.assertEqual(len(calls), 1)

    def test_missing_artifact_refuses_install(self):
        approved, _ = self.package.review()
        metadata = subprocess.CompletedProcess([], 0, str(self.root / 'missing.pkg.tar.zst') + '\n', '')
        with patch.object(self.package, 'prepare'), patch.object(w.subprocess, 'run', return_value=subprocess.CompletedProcess([], 0)) as commands, patch.object(w, 'run', return_value=metadata), patch('builtins.input') as prompt, self.assertRaises(w.Error):
            w.build_install(self.package, approved, self.store)
        prompt.assert_not_called()
        self.assertEqual(commands.call_count, 1)
        self.assertFalse(self.store.path.exists())

    def test_checkout_changed_after_review_requires_new_approval(self):
        self.advance()
        self.package.fetch()
        approved, _ = self.package.review()
        git(self.checkout, 'merge', '--ff-only', approved)
        with self.assertRaises(w.Error):
            self.package.prepare(approved)

    def test_local_change_invalidates_approval(self):
        local = self.root / 'local'
        local.mkdir()
        (local / 'PKGBUILD').write_text('pkgver=1\n')
        p = w.Package(local)
        approved, _ = p.review()
        (local / 'PKGBUILD').write_text('pkgver=2\n')
        with self.assertRaises(w.Error):
            p.prepare(approved)

    def test_terminal_controls_are_escaped(self):
        self.assertEqual(w.safe('\x1b[31mhello\x00'), r'\x1b[31mhello\x00')


if __name__ == '__main__':
    unittest.main()
