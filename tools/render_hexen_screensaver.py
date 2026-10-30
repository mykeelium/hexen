#!/usr/bin/env python3
"""Rasterize the HEX3N display font into animated full-block-cell artwork."""
import argparse
from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FONT = ROOT / "config/fonts/HexenGlyphs-Regular.ttf"
DEFAULT_OUTPUT = ROOT / "config/branding/screensaver.txt"
WORDMARK = "HEX3N"
DOT_WIDTH = 128
DOT_HEIGHT = 36
ART_WIDTH = 110
ART_HEIGHT = 26
GLYPH_HORIZONTAL_SCALE = {"E": 0.78, "3": 0.78}
LETTER_GAPS = (36, 60, 60, 36)
BRAILLE_DOTS = (
    (0, 0, 0), (0, 1, 1), (0, 2, 2),
    (1, 0, 3), (1, 1, 4), (1, 2, 5),
    (0, 3, 6), (1, 3, 7),
)


def fallback_font_path():
    result = subprocess.run(
        ["fc-match", "-f", "%{file}", "JetBrainsMono Nerd Font"],
        check=True, capture_output=True, text=True,
    )
    path = Path(result.stdout.strip())
    if not path.is_file():
        raise RuntimeError("fontconfig could not locate JetBrainsMono Nerd Font")
    return path


def glyph_image(font, character, cap_height, advance, horizontal_scale=1.0):
    bounds = font.getbbox(character)
    glyph = Image.new("L", (bounds[2] - bounds[0], bounds[3] - bounds[1]), 0)
    ImageDraw.Draw(glyph).text((-bounds[0], -bounds[1]), character, font=font, fill=255)
    width = round(glyph.width * cap_height / glyph.height * horizontal_scale)
    if glyph.height != cap_height or width != glyph.width:
        glyph = glyph.resize((width, cap_height), Image.Resampling.LANCZOS)
    cell = Image.new("L", (advance, cap_height), 0)
    cell.paste(glyph, ((advance - glyph.width) // 2, 0))
    return cell


def compose_wordmark(custom_font_path, fallback_font_file, wordmark=WORDMARK):
    """Compose trimmed glyph outlines with tight, mirrored gaps around X."""
    if wordmark != WORDMARK:
        raise ValueError("wordmark layout is defined for HEX3N")
    custom = ImageFont.truetype(str(custom_font_path), 1000)
    fallback = ImageFont.truetype(str(fallback_font_file), 1000)
    bounds = custom.getbbox("H")
    cap_height = bounds[3] - bounds[1]
    advance = round(custom.getlength("H"))
    glyphs = []
    for character in wordmark:
        font = custom if character in "HEN3" else fallback
        cell = glyph_image(
            font, character, cap_height, advance,
            horizontal_scale=GLYPH_HORIZONTAL_SCALE.get(character, 1.0),
        )
        ink_bounds = cell.getbbox()
        glyphs.append(cell.crop((ink_bounds[0], 0, ink_bounds[2], cap_height)))

    width = sum(glyph.width for glyph in glyphs) + sum(LETTER_GAPS)
    composition = Image.new("L", (width, cap_height), 0)
    x = 0
    for index, glyph in enumerate(glyphs):
        composition.paste(glyph, (x, 0))
        x += glyph.width
        if index < len(LETTER_GAPS):
            x += LETTER_GAPS[index]
    return composition


def render_art(custom_font_path, fallback_font_file, wordmark=WORDMARK):
    """Return a fixed 64x9 full-block grid sampled from the wordmark glyphs."""
    if not wordmark or any(character not in "HEN3X" for character in wordmark):
        raise ValueError("wordmark may contain only H, E, X, 3, and N")
    if DOT_WIDTH % 2 or DOT_HEIGHT % 4:
        raise ValueError("Braille raster dimensions must be divisible by 2 by 4")

    composition = compose_wordmark(custom_font_path, fallback_font_file, wordmark)
    # Keep the prior 26-dot glyph height, trim the E/X and X/3 gaps, and leave
    # a centered margin around the narrower artwork on the fixed-width canvas.
    raster = composition.resize((ART_WIDTH, ART_HEIGHT), Image.Resampling.LANCZOS)
    canvas = Image.new("L", (DOT_WIDTH, DOT_HEIGHT), 0)
    canvas.paste(raster, ((DOT_WIDTH - raster.width) // 2,
                          (DOT_HEIGHT - raster.height) // 2))

    pixels = canvas.load()
    lines = []
    for y in range(0, DOT_HEIGHT, 4):
        row = []
        for x in range(0, DOT_WIDTH, 2):
            mask = 0
            for dot_x, dot_y, bit in BRAILLE_DOTS:
                if pixels[x + dot_x, y + dot_y] >= 96:
                    mask |= 1 << bit
            # A Braille blank preserves one-cell spacing without visible dots.
            row.append("█" if mask else "⠀")
        lines.append("".join(row))
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--font", type=Path, default=DEFAULT_FONT,
                        help="built HEXEN glyph font")
    parser.add_argument("--fallback-font", type=Path, default=None,
                        help="font file to use for X (default: fontconfig's JetBrainsMono Nerd Font)")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT,
                        help="generated screensaver artwork")
    args = parser.parse_args()
    fallback = args.fallback_font or fallback_font_path()
    art = render_art(args.font, fallback)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(art, encoding="utf-8")
    print(f"Generated {args.output} (64 columns x 9 rows)")


if __name__ == "__main__":
    main()
