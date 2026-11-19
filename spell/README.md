# The composer's English dictionary

Everything here is local. Nothing is fetched when the page runs.

| file        | what it is                                                       |
|-------------|------------------------------------------------------------------|
| `en_US.aff` | the Hunspell affix rules (plurals, -ing, -ed, -ly, comparison …)   |
| `en_US.dic` | the 49,000-word SCOWL en_US list the rules apply to               |
| `nspell.js` | [nspell](https://github.com/wooorm/nspell) (MIT) bundled into one 10 KB script that sets `window.NSpell` |

`tools/build_spell.py` compiles the two Hunspell files plus Fluentify's own
taught vocabulary into `spell.json` (the `extra` list). That file is what both
builds read: the web page through `/api/spell`, the APK through
`data/spell.json`. Rebuild it after replacing a dictionary:

```
python3 tools/build_spell.py
python3 tools/check_spell.py     # and this proves spell.json is not stale
```

`en_US.aff` and `en_US.dic` are the SCOWL en_US set as shipped by the
Debian/Ubuntu `hunspell-en-us` package (Copyright 2000–2018 Kevin Atkinson;
the package's `copyright` file is the authoritative licence text: it is
distributed under the SCOWL licence, which permits use, modification and
redistribution, including in a product such as this one).

To rebuild `nspell.js` after upgrading nspell:

```
mkdir -p /tmp/spellbuild && cd /tmp/spellbuild
npm i nspell@2.1.5 esbuild
printf "import nspell from 'nspell';\nconst g = (typeof window !== 'undefined') ? window : globalThis;\ng.NSpell = nspell;\n" > entry.js
npx esbuild entry.js --bundle --format=iife --minify --outfile=spell.js
cp spell.js <repo>/spell/nspell.js
```
