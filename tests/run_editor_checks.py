"""Run assertions after a real Neovim UI attaches, using a temporary Lua file."""
import argparse
from contextlib import suppress
from pathlib import Path
import tempfile

import pynvim


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--init', help='alternate init.lua for isolated validation')
    parser.add_argument('--pins-only', action='store_true', help='validate bootstrap before language-tool setup')
    args = parser.parse_args()
    tests = Path(__file__).resolve().parent
    with tempfile.TemporaryDirectory(prefix='hexen-editor-check-') as directory:
        fixture = Path(directory) / 'smoke.lua'
        fixture.write_text('-- Temporary Hexen editor acceptance buffer\n')
        command = ['nvim', '--embed']
        if args.init:
            command.extend(['-u', args.init])
        command.append(str(fixture))
        editor = pynvim.attach('child', argv=command)
        try:
            editor.ui_attach(100, 30, rgb=True)
            editor.exec_lua('''
                assert(vim.wait(10000, function()
                    return vim.g.did_very_lazy and vim.fn.exists(':DapKeys') == 2
                end, 50), 'Editor UI startup did not finish')
            ''')
            scripts = ['nvim-pins.lua']
            if not args.pins_only:
                scripts.extend(['nvim.lua', 'editor-project.lua'])
            for name in scripts:
                editor.exec_lua('dofile(...)', str(tests / name))
                print(name + ': passed', flush=True)
        finally:
            with suppress(EOFError, OSError):
                editor.command('qa!')
            editor.close()


if __name__ == '__main__':
    main()
