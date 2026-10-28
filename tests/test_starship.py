"""Verify the installed prompt's user-visible output against a disposable repo."""
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

CONFIG = Path(__file__).resolve().parents[1] / 'config/starship.toml'
ANSI = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')


@unittest.skipUnless(shutil.which('starship'), 'Install the declared Starship dependency first')
class StarshipPromptTest(unittest.TestCase):
    def test_prompt_shows_directory_branch_untracked_file_and_command_status(self):
        self.assertTrue(CONFIG.is_file(), 'Install must include the Starship configuration')
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            repo = root / 'hexen-prompt-test'
            repo.mkdir()
            subprocess.run(['git', 'init', '-q', '-b', 'main', str(repo)], check=True)
            (repo / 'example.txt').write_text('untracked fixture\n')
            env = {**os.environ, 'STARSHIP_CONFIG': str(CONFIG), 'STARSHIP_CACHE': str(root / 'cache'),
                   'STARSHIP_LOG': 'warn', 'TERM': 'xterm-256color', 'PWD': str(repo)}
            for status, symbol in [(0, '❯'), (1, '✗')]:
                result = subprocess.run(['starship', 'prompt', '--path', str(repo), '--status', str(status)],
                    env=env, cwd=repo, capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, '')
                prompt = ANSI.sub('', result.stdout)
                self.assertIn('hexen-prompt-test', prompt)
                self.assertIn('main', prompt)
                self.assertIn('?', prompt)
                self.assertIn(symbol, prompt)


if __name__ == '__main__': unittest.main()
