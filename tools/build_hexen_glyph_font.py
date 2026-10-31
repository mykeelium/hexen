#!/usr/bin/env python3
"""Build the HEXEN display font from the owner-provided SVG paths."""
import argparse
from pathlib import Path
import xml.etree.ElementTree as ET

from fontTools.fontBuilder import FontBuilder
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.cu2quPen import Cu2QuPen
from fontTools.pens.reverseContourPen import ReverseContourPen
from fontTools.pens.transformPen import TransformPen
from fontTools.pens.ttGlyphPen import TTGlyphPen
from fontTools.svgLib.path import parse_path

ROOT = Path(__file__).resolve().parents[1]
SVG_HN = ROOT / "assets/hexen_h_and_n.svg"
SVG_E3 = ROOT / "assets/hexen_e_and_3.svg"
DEFAULT_OUTPUT = ROOT / "config/fonts/HexenGlyphs-Regular.ttf"
SVG_NS = "http://www.w3.org/2000/svg"
UNITS_PER_EM = 1000
CAP_HEIGHT = 700
SIDE_BEARING = 24
ADVANCE = 850
GLYPH_WIDTH = ADVANCE - 2 * SIDE_BEARING


def empty_glyph():
    return TTGlyphPen(None).glyph()


def notdef_glyph():
    pen = TTGlyphPen(None)
    pen.moveTo((80, 0))
    pen.lineTo((770, 0))
    pen.lineTo((770, 700))
    pen.lineTo((80, 700))
    pen.closePath()
    pen.moveTo((150, 70))
    pen.lineTo((150, 630))
    pen.lineTo((700, 630))
    pen.lineTo((700, 70))
    pen.closePath()
    return pen.glyph()


def glyph_from_svg_path(path_data):
    bounds_pen = BoundsPen(None)
    parse_path(path_data, bounds_pen)
    if bounds_pen.bounds is None:
        raise ValueError("SVG glyph path has no drawable outline")
    x_min, y_min, x_max, y_max = bounds_pen.bounds
    if x_max <= x_min or y_max <= y_min:
        raise ValueError("SVG glyph path has empty or degenerate bounds")
    x_scale = GLYPH_WIDTH / (x_max - x_min)
    y_scale = CAP_HEIGHT / (y_max - y_min)
    pen = TTGlyphPen(None)
    quadratic_pen = Cu2QuPen(pen, max_err=1, all_quadratic=True)
    transform = TransformPen(
        quadratic_pen,
        (x_scale, 0, 0, -y_scale, SIDE_BEARING - x_min * x_scale, y_max * y_scale),
    )
    parse_path(path_data, transform)
    return pen.glyph()


def normalize_glyph(glyph):
    """Fit every custom outline to one shared box with equal side bearings."""
    coordinates = glyph.coordinates
    x_min = min(point[0] for point in coordinates)
    y_min = min(point[1] for point in coordinates)
    x_max = max(point[0] for point in coordinates)
    y_max = max(point[1] for point in coordinates)
    if x_max <= x_min or y_max <= y_min:
        raise ValueError("SVG glyph path has empty or degenerate bounds")
    x_scale = GLYPH_WIDTH / (x_max - x_min)
    y_scale = CAP_HEIGHT / (y_max - y_min)
    for index, (x, y) in enumerate(coordinates):
        coordinates[index] = (
            round(SIDE_BEARING + (x - x_min) * x_scale),
            round((y - y_min) * y_scale),
        )
    return glyph


def mirrored_glyph(glyph):
    """Reflect an outline across the center of its advance, preserving winding."""
    pen = TTGlyphPen(None)
    reflected = TransformPen(pen, (-1, 0, 0, 1, ADVANCE, 0))
    glyph.draw(ReverseContourPen(reflected), None)
    return pen.glyph()


def build(output):
    def ordered_paths(svg, expected):
        root = ET.parse(svg).getroot()
        paths = root.findall(f".//{{{SVG_NS}}}path")
        if len(paths) != 2 or any(not item.get("d") for item in paths):
            raise ValueError(f"expected exactly two SVG paths in {svg.name}, ordered {expected}")
        return [item.get("d") for item in paths]

    h_path, _n_reference = ordered_paths(SVG_HN, "H then N")
    e_path, _three_reference = ordered_paths(SVG_E3, "E then 3")

    glyph_order = [".notdef", "space", "H", "N", "E", "three"]
    h_glyph = normalize_glyph(glyph_from_svg_path(h_path))
    e_glyph = normalize_glyph(glyph_from_svg_path(e_path))
    glyphs = {
        ".notdef": notdef_glyph(),
        "space": empty_glyph(),
        # Uniform outlines fill the same advance. The right-side letters are
        # exact reflections, avoiding asymmetric rounding in SVG curve conversion.
        "H": h_glyph,
        "N": mirrored_glyph(h_glyph),
        "E": e_glyph,
        "three": mirrored_glyph(e_glyph),
    }
    fb = FontBuilder(UNITS_PER_EM, isTTF=True)
    fb.setupGlyphOrder(glyph_order)
    fb.setupCharacterMap({0x20: "space", 0x33: "three", 0x45: "E", 0x48: "H", 0x4E: "N"})
    fb.setupGlyf(glyphs)
    metrics = {name: (ADVANCE, SIDE_BEARING) for name in ("H", "N", "E", "three")}
    metrics.update({".notdef": (ADVANCE, 80), "space": (ADVANCE, 0)})
    fb.setupHorizontalMetrics(metrics)
    fb.setupHorizontalHeader(ascent=800, descent=-200)
    fb.setupNameTable({
        "familyName": "Hexen Glyphs",
        "styleName": "Regular",
        "uniqueFontIdentifier": "Hexen Glyphs Regular 1.001",
        "fullName": "Hexen Glyphs Regular",
        "psName": "HexenGlyphs-Regular",
        "version": "Version 1.001",
    })
    fb.setupOS2(
        sTypoAscender=800,
        sTypoDescender=-200,
        sTypoLineGap=0,
        usWinAscent=800,
        usWinDescent=200,
        sxHeight=500,
        sCapHeight=CAP_HEIGHT,
        usWeightClass=400,
    )
    fb.setupPost(isFixedPitch=1)
    fb.setupMaxp()
    font = fb.font
    # Fixed timestamps keep a rebuild from changing the binary for metadata alone.
    font["head"].created = font["head"].modified = 2082844800
    output.parent.mkdir(parents=True, exist_ok=True)
    font.save(output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    build(args.output)
    print(f"Built {args.output}")


if __name__ == "__main__":
    main()
