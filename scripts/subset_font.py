#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont


# Ranges removed by the relaxed terminal profile. Everything else encoded by
# the source font is retained by default.
DROP_RANGES = [
    (0xAC00, 0xD7AF, "Hangul Syllables"),
    (0x20000, 0x2A6DF, "CJK Unified Ideographs Extension B"),
    (0x2A700, 0x2B73F, "CJK Unified Ideographs Extension C"),
    (0x2B740, 0x2B81F, "CJK Unified Ideographs Extension D"),
    (0x2B820, 0x2CEAF, "CJK Unified Ideographs Extension E"),
    (0x2CEB0, 0x2EBEF, "CJK Unified Ideographs Extension F"),
    (0x2EBF0, 0x2EE5F, "CJK Unified Ideographs Extension I"),
    (0x30000, 0x3134F, "CJK Unified Ideographs Extension G"),
    (0x31350, 0x323AF, "CJK Unified Ideographs Extension H"),
]


def euc_kr_codepoints() -> set[int]:
    """Return characters representable in EUC-KR.

    This restores the common KS X 1001 Korean repertoire (including its common
    precomposed Hangul syllables) after the broad Hangul-syllable exclusion.
    """
    result: set[int] = set(range(0x80))
    for lead in range(0xA1, 0xFF):
        for trail in range(0xA1, 0xFF):
            try:
                s = bytes((lead, trail)).decode("euc_kr")
            except UnicodeDecodeError:
                continue
            if len(s) == 1:
                result.add(ord(s))
    return result


def in_drop_range(cp: int) -> bool:
    return any(lo <= cp <= hi for lo, hi, _ in DROP_RANGES)


def count_in_range(codepoints: set[int], lo: int, hi: int) -> int:
    return sum(lo <= cp <= hi for cp in codepoints)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument(
        "--profile",
        default="terminal-sc-relaxed",
        choices=["terminal-sc-relaxed"],
    )
    args = ap.parse_args()

    src = TTFont(args.input, recalcTimestamp=False)
    cmap = src.getBestCmap() or {}
    original_cps = set(cmap)
    before_glyphs = src["maxp"].numGlyphs

    # Preserve everything by default, then remove only known high-cost ranges.
    keep = {cp for cp in original_cps if not in_drop_range(cp)}

    # Restore common Korean characters/syllables covered by EUC-KR.
    kr_restore = original_cps & euc_kr_codepoints()
    keep |= kr_restore

    options = subset.Options()
    # Preserve all source OpenType layout behavior that remains reachable from
    # the retained repertoire, rather than maintaining a feature whitelist.
    options.layout_features = ["*"]
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
    after_cps = set(after_cmap)
    after_glyphs = check["maxp"].numGlyphs
    dropped = original_cps - after_cps

    print(f"subset profile: {args.profile}")
    print("policy: retain all source codepoints except explicit high-cost ranges")
    print("OpenType layout features: * (all reachable features)")
    print(f"glyphs: {before_glyphs} -> {after_glyphs}")
    print(f"encoded codepoints: {len(original_cps)} -> {len(after_cps)}")
    print(f"dropped encoded codepoints: {len(dropped)}")
    print(f"EUC-KR codepoints restored/retained: {len(kr_restore)}")
    for lo, hi, name in DROP_RANGES:
        original_count = count_in_range(original_cps, lo, hi)
        kept_count = count_in_range(after_cps, lo, hi)
        print(
            f"range {name} U+{lo:04X}-U+{hi:04X}: "
            f"source={original_count}, retained={kept_count}, "
            f"dropped={original_count - kept_count}"
        )
    print(f"output: {out}")


if __name__ == "__main__":
    main()
