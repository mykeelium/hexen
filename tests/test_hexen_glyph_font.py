"""Verify the custom HEXEN glyph font and Ghostty fallback configuration."""
from pathlib import Path
import unittest
from PIL import ImageFont

try:
    from fontTools.ttLib import TTFont
except ImportError:
    TTFont = None

ROOT = Path(__file__).resolve().parents[1]
FONT = ROOT / "config/fonts/HexenGlyphs-Regular.ttf"


class HexenGlyphFontTest(unittest.TestCase):
    @unittest.skipIf(TTFont is None, "FontTools is needed to inspect generated glyph outlines")
    def test_font_maps_ascii_h_n_e_and_three_to_distinct_custom_outlines(self):
        font = TTFont(FONT)
        cmap = font.getBestCmap()
        for character, glyph in (("H", "H"), ("N", "N"), ("E", "E"), ("3", "three")):
            self.assertEqual(cmap.get(ord(character)), glyph)
        self.assertNotIn(ord("X"), cmap)
        for glyph in ("H", "N", "E", "three"):
            self.assertGreater(font["glyf"][glyph].numberOfContours, 0)
        self.assertNotEqual(font["glyf"]["E"].coordinates, font["glyf"]["three"].coordinates)
        self.assertTrue(all(font["hmtx"][glyph][0] > 0 for glyph in ("H", "N", "E", "three")))

    @unittest.skipIf(TTFont is None, "FontTools is needed to inspect generated glyph outlines")
    def test_mirror_pairs_have_identical_bounds_and_exact_reflected_points(self):
        font = TTFont(FONT)
        for left, right in (("H", "N"), ("E", "three")):
            left_glyph = font["glyf"][left]
            right_glyph = font["glyf"][right]
            self.assertEqual(
                (left_glyph.xMin, left_glyph.yMin, left_glyph.xMax, left_glyph.yMax),
                (right_glyph.xMin, right_glyph.yMin, right_glyph.xMax, right_glyph.yMax),
            )
            axis_twice = left_glyph.xMin + left_glyph.xMax
            reflected = {(axis_twice - x, y) for x, y in left_glyph.coordinates}
            self.assertEqual(reflected, set(right_glyph.coordinates))

    @unittest.skipIf(TTFont is None, "FontTools is needed to inspect generated glyph metrics")
    def test_custom_glyphs_have_consistent_side_bearings_and_cell_widths(self):
        font = TTFont(FONT)
        widths = set()
        bounds = set()
        for name in ("H", "N", "E", "three"):
            glyph = font["glyf"][name]
            advance, left_bearing = font["hmtx"][name]
            self.assertEqual(left_bearing, 24)
            widths.add(glyph.xMax - glyph.xMin)
            bounds.add((glyph.xMin, glyph.yMin, glyph.xMax, glyph.yMax))
            self.assertEqual(advance - (glyph.xMax - glyph.xMin), 48)
        self.assertEqual(len(widths), 1)
        self.assertEqual(len(bounds), 1)

    def test_screensaver_uses_custom_font_then_regular_font_fallback(self):
        config = (ROOT / "config/ghostty/screensaver.ghostty").read_text()
        families = [line.partition("=")[2].strip().strip('"')
                    for line in config.splitlines() if line.startswith("font-family")]
        self.assertEqual(families[:2], ["Hexen Glyphs", "JetBrainsMono Nerd Font"])
        self.assertIn("font-size = 18", config.splitlines())
        art = (ROOT / "config/branding/screensaver.txt").read_text().splitlines()
        self.assertEqual(len(art), 9)
        self.assertTrue(all(len(row) == 64 for row in art))
        self.assertTrue(all(all(char in {"█", "⠀"} for char in row) for row in art))
        self.assertTrue(any("█" in row for row in art))

    def test_screensaver_art_is_generated_from_custom_glyphs_and_fallback_x(self):
        from tools.render_hexen_screensaver import compose_wordmark, glyph_image, render_art
        generated = render_art(FONT, Path("/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf"))
        checked_in = (ROOT / "config/branding/screensaver.txt").read_text().rstrip("\n")
        self.assertEqual(generated.rstrip("\n"), checked_in)

        font = ImageFont.truetype(str(FONT), 1000)
        bounds = font.getbbox("H")
        cap_height = bounds[3] - bounds[1]
        advance = round(font.getlength("H"))
        full_width = glyph_image(font, "H", cap_height, advance).getbbox()[2]
        narrow_e = glyph_image(font, "E", cap_height, advance, horizontal_scale=0.78)
        narrow_three = glyph_image(font, "3", cap_height, advance, horizontal_scale=0.78)
        self.assertLess(narrow_e.getbbox()[2] - narrow_e.getbbox()[0], full_width)
        self.assertEqual(narrow_e.getbbox()[2] - narrow_e.getbbox()[0],
                         narrow_three.getbbox()[2] - narrow_three.getbbox()[0])
        self.assertLess(compose_wordmark(FONT, Path("/usr/share/fonts/TTF/JetBrainsMonoNerdFont-Regular.ttf")).width,
                        5 * advance)

    def test_lock_screen_wordmark_uses_custom_glyph_family(self):
        config = (ROOT / "config/hypr/hyprlock.conf").read_text()
        wordmark = config.split("text = HEX3N", 1)[1].split("}", 1)[0]
        self.assertIn("font_family = Hexen Glyphs", wordmark)
        self.assertIn("font_size = 68", wordmark)


if __name__ == "__main__":
    unittest.main()
