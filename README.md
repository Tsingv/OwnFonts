# OwnFonts

Terminal-oriented CJK Nerd Font builds, generated automatically from upstream
releases.

## Built families

| Family | Upstream files selected | Pre-processing |
| --- | --- | --- |
| Sarasa Term SC | Regular, Bold | `terminal-sc-relaxed` subset |
| LXGW WenKai GB | Regular, Medium | none |
| LXGW WenKai Mono GB | Regular, Medium | none |
| LXGW Neo XiHei | normal, Plus | none |

Every selected source font is built twice:

- **Nerd Font** — complete current Nerd Fonts symbol set, normal icon widths.
- **Nerd Font Mono** — complete current symbol set with added icons constrained
  to single-cell width.

The Mono build deliberately uses Nerd Fonts' `--single-width-glyphs`, **not**
`--mono`; CJK source glyph widths are therefore not globally forced to one
cell.

## Source glyphs win

The patcher is always run with:

```text
--complete --careful
```

`--complete` enables all current Nerd Fonts glyph sets. `--careful` prevents
the patcher from replacing an encoded glyph already present in the source font.
The build then verifies that:

1. every encoded codepoint in the prepared source survives;
2. every encoded codepoint in the matching official Symbols Nerd Font is
   present;
3. `U+F01BC` (`md-database`, 󰆼) is present;
4. the result stays below the 65,535-glyph OpenType limit.

A failed check blocks the release instead of silently publishing an incomplete
font.

## Why Sarasa is subsetted

Sarasa Term SC is already a very large CJK font. Adding the complete Nerd Fonts
symbol set can push a single TTF past the OpenType glyph-count limit.

The `terminal-sc-relaxed` profile is deliberately conservative: it starts by
keeping **all encoded source characters** and removes only the largest,
least-terminal-oriented repertoires needed to make room for the complete Nerd
Fonts symbol set.

Currently it removes:

- most precomposed Hangul syllables (`U+AC00–U+D7AF`);
- CJK Unified Ideographs Extensions B, C, D, E, F, G, H and I.

Common Korean text is not removed wholesale: characters representable by
EUC-KR (the KS X 1001 repertoire, including common precomposed Hangul
syllables) are added back. Hangul Jamo, Compatibility Jamo, non-CJK scripts,
symbols, source PUA characters and other source Unicode coverage are retained
unless they fall inside one of the explicit removal ranges.

All reachable OpenType layout features are preserved with `layout_features=*`
instead of maintaining a feature whitelist. This subset is still intentionally
**not** advertised as a byte-for-byte or repertoire-identical replacement for
the full upstream Sarasa font.

LXGW WenKai GB and LXGW Neo XiHei are patched without subsetting unless they
eventually exceed the limit; the verification step will catch that.

## Automation

GitHub Actions checks the latest releases of:

- `be5invis/Sarasa-Gothic`
- `lxgw/LxgwWenkaiGB`
- `lxgw/LxgwNeoXiHei`
- `ryanoasis/nerd-fonts`

on a daily schedule. A deterministic release tag contains all four upstream
versions, so unchanged inputs are skipped. Updating Nerd Fonts alone also
triggers a rebuild, which keeps the icon set current.

The workflow can also be run manually with **force rebuild** enabled.

Font selection is controlled by [`config/fonts.json`](config/fonts.json).
See [`LICENSES.md`](LICENSES.md) for upstream licensing notes.
