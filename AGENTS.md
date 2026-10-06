# AGENTS.md

This repository builds patched CJK Nerd Fonts from upstream releases. Agents
working here should optimize for correctness, source-font fidelity, and
reproducible CI rather than minimizing build time or file size.

## Core invariants

1. **Source glyphs win.** Nerd Fonts must be patched with `--careful` (or an
   equivalent mechanism) so an encoded glyph already present in the prepared
   source font is not silently replaced.
2. **Complete Nerd Symbols are required.** Use the current Nerd Fonts complete
   symbol set and verify output coverage against the matching official
   `SymbolsNerdFont-Regular.ttf` / `SymbolsNerdFontMono-Regular.ttf`.
   Do not silently omit Material Design Icons or other sets to make a build
   pass.
3. **U+F01BC is a sentinel.** Every published NF/NFM output must contain
   `U+F01BC` (`md-database`, 󰆼). Failure is release-blocking.
4. **Do not force CJK fonts globally monospaced.** For the Nerd Font Mono
   variant use `--single-width-glyphs` for added symbols. Do not use
   `--mono` / `-s` unless a future change explicitly demonstrates that it
   does not damage CJK double-cell widths and documents why.
5. **Preserve source metrics and layout behavior.** Avoid options that globally
   rewrite line height, advance widths, or source glyph metrics without a
   demonstrated need. When subsetting, preserve all reachable OpenType layout
   features unless there is a measured glyph-limit reason not to.
6. **Never publish an over-limit or partially verified font.** The OpenType
   glyph limit is 65,535. A failed glyph-count, source-retention, symbol
   coverage, or sentinel check must fail CI.

## Subsetting policy

Subsetting is a last-mile capacity tool, not a general size optimization.

- Do not subset a family that fits the complete Nerd Fonts set unless there is
  a concrete reason.
- Sarasa Term SC currently uses the `terminal-sc-relaxed` profile.
- That profile should retain all source Unicode coverage by default and remove
  only explicitly documented high-cost ranges.
- Current intentional removals are most Hangul syllables plus CJK Unified
  Ideographs Extensions B-I. Common EUC-KR/KS X 1001 Korean characters are
  restored.
- Prefer adding back useful coverage when glyph headroom allows it.
- Any new removal range must be documented in `README.md`, printed in the CI
  report, and justified by measured glyph pressure.
- Never silently reduce BMP CJK, GBK/common Simplified Chinese, ASCII/Latin,
  terminal drawing characters, source PUA, or Nerd Fonts coverage.
- If an upstream update pushes a font near the glyph limit, inspect actual
  range counts first. Make the smallest targeted reduction that restores safe
  headroom.

## Verification and reporting

Every changed build should be validated through GitHub Actions with real
upstream release assets. Do not treat a successful FontForge exit code alone
as success.

Reports should retain at least:

- prepared-source glyph and encoded-codepoint counts;
- patched glyph and encoded-codepoint counts;
- official Symbols Nerd Font codepoint count;
- number of source/symbol overlaps protected by source-first behavior;
- explicit U+F01BC result;
- per-range subset counts when subsetting is used;
- final glyph headroom versus 65,535.

When changing subset logic, compare the new Sarasa prepared/patched counts with
the previous release and summarize what coverage was gained or lost.

## CI and releases

- Track upstream latest releases of Sarasa Gothic, LXGW WenKai GB, LXGW Neo
  XiHei, and Nerd Fonts.
- A Nerd Fonts version change is a rebuild-worthy input even when source-font
  versions are unchanged.
- Keep scheduled builds idempotent: unchanged inputs/configuration should not
  create duplicate releases.
- Superseded builds may be cancelled so only the latest repository revision
  publishes.
- Generated font binaries belong in GitHub Release assets, not in the Git
  repository.
- Keep per-family reports attached to releases.
- Do not weaken verification merely to get a release green.

## Family selection

The authoritative family/source selection is `config/fonts.json`. Prefer
changing that file instead of hard-coding additional font filenames in the
workflow.

When adding a family or weight:

- confirm the upstream license permits redistribution of the generated font;
- add/update licensing notes;
- verify the release asset/file regex against a real upstream release;
- ensure both NF and NFM outputs pass the same checks.

## Change style

Keep scripts straightforward and auditable. Prefer explicit Unicode ranges and
named policies over opaque heuristics. Comments should explain *why* a range or
patcher option exists, especially when it affects repertoire or metrics.
