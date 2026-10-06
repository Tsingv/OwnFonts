#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont


TERMINAL_RANGES = [
    (0x0000, 0x024F),  # Basic Latin, Latin-1, Latin Extended
    (0x0250, 0x02FF),  # IPA + spacing modifiers
    (0x0300, 0x036F),  # Combining marks
    (0x0370, 0x03FF),  # Greek
    (0x0400, 0x052F),  # Cyrillic
    (0x2000, 0x206F),  # General punctuation
    (0x2070, 0x209F),  # Super/subscripts
    (0x20A0, 0x20CF),  # Currency
    (0x2100, 0x214F),  # Letterlike
    (0x2150, 0x218F),  # Number forms
    (0x2190, 0x21FF),  # Arrows
    (0x2200, 0x22FF),  # Math
    (0x2300, 0x23FF),  # Technical
    (0x2400, 0x245F),  # Control pictures + OCR
    (0x2460, 0x24FF),  # Enclosed alphanumerics
    (0x2500, 0x257F),  # Box drawing
    (0x2580, 0x259F),  # Block elements
    (0x25A0, 0x25FF),  # Geometric shapes
    (0x2600, 0x26FF),  # Misc symbols
    (0x2700, 0x27BF),  # Dingbats
    (0x27C0, 0x27FF),  # Math/arrow supplements
    (0x2800, 0x28FF),  # Braille
    (0x2900, 0x297F),  # Supplemental arrows
    (0x2B00, 0x2BFF),  # Misc symbols and arrows
    (0x2E80, 0x2EFF),  # CJK radicals supplement
    (0x2F00, 0x2FDF),  # Kangxi radicals
    (0x2FF0, 0x2FFF),  # Ideographic description chars
    (0x3000, 0x303F),  # CJK punctuation
    (0x3040, 0x309F),  # Hiragana
    (0x30A0, 0x30FF),  # Katakana
    (0x3100, 0x312F),  # Bopomofo
    (0x31A0, 0x31BF),  # Bopomofo Extended
    (0x31C0, 0x31EF),  # CJK strokes
    (0x31F0, 0x31FF),  # Katakana extensions
    (0x3200, 0x33FF),  # Enclosed/compatibility CJK
    (0x3400, 0x4DBF),  # CJK Extension A
    (0x4E00, 0x9FFF),  # CJK Unified Ideographs
    (0xF900, 0xFAFF),  # CJK Compatibility Ideographs
    (0xFE00, 0xFE0F),  # Variation selectors
    (0xFE10, 0xFE1F),  # Vertical forms
    (0xFE30, 0xFE4F),  # CJK compatibility forms
    (0xFE50, 0xFE6F),  # Small forms
    (0xFF00, 0xFFEF),  # Half/full width
]


def gbk_codepoints() -> set[int]:
    result: set[int] = set()
    for b in range(0x80):
        result.add(b)
    for lead in range(0x81, 0xFF):
        for trail in range(0x40, 0xFF):
            if trail == 0x7F:
                continue
            try:
                s = bytes((lead, trail)).decode("gbk")
            except UnicodeDecodeError:
                continue
            if len(s) == 1:
                result.add(ord(s))
    return result


def is_pua(cp: int) -> bool:
    return (
        0xE000 <= cp <= 0xF8FF
        or 0xF0000 <= cp <= 0xFFFFD
        or 0x100000 <= cp <= 0x10FFFD
    )


def in_ranges(cp: int) -> bool:
    return any(lo <= cp <= hi for lo, hi in TERMINAL_RANGES)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--profile", default="terminal-sc", choices=["terminal-sc"])
    args = ap.parse_args()

    src = TTFont(args.input, recalcTimestamp=False)
    cmap = src.getBestCmap() or {}
    original_cps = set(cmap)
    before_glyphs = src["maxp"].numGlyphs

    keep = {cp for cp in original_cps if in_ranges(cp) or is_pua(cp)}
    keep |= original_cps & gbk_codepoints()
    keep |= {cp for cp in original_cps if 0xE0100 <= cp <= 0xE01EF}

    options = subset.Options()
    options.layout_features = [
        "ccmp", "locl", "liga", "clig", "calt", "kern", "mark", "mkmk"
    ]
    options.glyph_names = True
    options.legacy_cmap = True
    options.symbol_cmap = True
    options.notdef_glyph = True
    options.notdef_outline = True
    options.recommended_glyphs = True
    options.recalc_timestamp = False

    sub = subset.Subsetter(options=options)
    sub.populate(unicodes=keep)
    sub.subset(src)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    src.save(out)

    check = TTFont(out)
    after_cmap = check.getBestCmap() or {}
    after_glyphs = check["maxp"].numGlyphs

    dropped = len(original_cps - set(after_cmap))
    print(f"subset profile: {args.profile}")
    print(f"glyphs: {before_glyphs} -> {after_glyphs}")
    print(f"encoded codepoints: {len(original_cps)} -> {len(after_cmap)}")
    print(f"dropped encoded codepoints: {dropped}")
    print(f"output: {out}")


if __name__ == "__main__":
    main()
