#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path

from fontTools.ttLib import TTFont


LIMIT = 65535
MD_DATABASE = 0xF01BC


def cmap(font: TTFont) -> dict[int, str]:
    return font.getBestCmap() or {}


def sample(values: set[int], n: int = 12) -> str:
    return ", ".join(f"U+{cp:04X}" for cp in sorted(values)[:n])


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", required=True)
    ap.add_argument("--patched", required=True)
    ap.add_argument("--symbols", required=True)
    ap.add_argument("--mode", choices=["nf", "nfm"], required=True)
    args = ap.parse_args()

    source = TTFont(args.source)
    patched = TTFont(args.patched)
    symbols = TTFont(args.symbols)

    src_map = cmap(source)
    out_map = cmap(patched)
    sym_map = cmap(symbols)

    src_cps = set(src_map)
    out_cps = set(out_map)
    sym_cps = set(sym_map)

    missing_source = src_cps - out_cps
    missing_symbols = sym_cps - out_cps
    overlaps = src_cps & sym_cps

    glyphs = patched["maxp"].numGlyphs
    failures: list[str] = []

    if missing_source:
        failures.append(
            f"lost {len(missing_source)} source codepoints: {sample(missing_source)}"
        )
    if missing_symbols:
        failures.append(
            f"missing {len(missing_symbols)} Nerd Symbols codepoints: "
            f"{sample(missing_symbols)}"
        )
    if MD_DATABASE not in out_cps:
        failures.append("U+F01BC md-database is missing")
    if glyphs > LIMIT:
        failures.append(f"glyph count {glyphs} exceeds OpenType limit {LIMIT}")

    print(f"mode: {args.mode}")
    print(f"source: {Path(args.source).name}")
    print(f"patched: {Path(args.patched).name}")
    print(f"source codepoints: {len(src_cps)}")
    print(f"symbol codepoints: {len(sym_cps)}")
    print(f"overlapping source/symbol codepoints kept by --careful: {len(overlaps)}")
    print(f"patched codepoints: {len(out_cps)}")
    print(f"patched glyphs: {glyphs}/{LIMIT}")
    print("U+F01BC md-database: present" if MD_DATABASE in out_cps else "U+F01BC: MISSING")

    if failures:
        for failure in failures:
            print(f"ERROR: {failure}")
        raise SystemExit(1)

    print("verification: OK")


if __name__ == "__main__":
    main()
