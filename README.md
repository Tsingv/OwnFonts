# OwnFonts

Terminal-oriented CJK Nerd Font builds, generated automatically from upstream
releases.

## Built families

| Family | Upstream files selected | Pre-processing |
| --- | --- | --- |
| Sarasa Term SC | Regular, Bold | `terminal-sc` subset |
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

The `terminal-sc` profile keeps a terminal-focused SC repertoire:

- Latin, Greek, Cyrillic, combining marks;
- common punctuation, arrows, math, box drawing, block elements and Braille;
- Hiragana, Katakana and Bopomofo;
- CJK Unified Ideographs and Extension A;
- CJK compatibility forms/ideographs;
- every character decodable through GBK that exists in the source;
- all source Private Use Area characters and variation selectors.

Large ranges that are not normally needed by a Simplified-Chinese terminal,
notably Hangul syllables and CJK Extension B+, are not retained unless covered
by one of the explicit preservation rules above. This subset is intentionally
**not** advertised as a drop-in replacement for the full upstream Sarasa font.

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
