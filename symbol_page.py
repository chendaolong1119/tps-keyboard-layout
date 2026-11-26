"""First symbol page shared by desktop (` then key) and phone (symbol key then key).

The page uses the same 41-key grid as the main layer:
  * digit row: digits;
  * TPS variants: placed by prefix_panel.panel (merged design);
  * common full-width punctuation fills the remaining keys by the rules below, so each layout
    gets its own page. Rules, in order:
      1. keep the key of the half-width symbol: ，on ,  。on .  ；on ;  ？on /  ——on -
      2. borrow the US Shift legends: ！under 1 (Q); （）under 9 0 (O P); ：beside ; (L)
      3. stack the paired brackets in the centre: 《》 over 「」 over 『』
      4. the rest on the left half: 、 … ～ ‧
    If a preferred key is taken, the nearest free key (or adjacent free pair) is used.
  * symbols that do not fit form a second row: the fifth row of the phone page (Taigi Keyboard's
    ?123 page already has five rows) and the second page of the desktop panel.
Usage: python symbol_page.py   (prints the pages; figures: python figures_symbol_page.py)"""
import json
from model import ROWS
from prefix_panel import panel, POS, DIGITS
from config import OUT

ITEMS = [  # (symbols, preferred key tuples)
    (('，',), [(',',)]), (('。',), [('.',)]), (('；',), [(';',)]), (('？',), [('/',)]),
    (('——',), [('-',)]),
    (('！',), [('q',)]), (('（', '）'), [('o', 'p')]), (('：',), [('l',)]),
    (('「', '」'), [('g', 'h')]), (('『', '』'), [('b', 'n')]), (('《', '》'), [('t', 'y')]),
    (('、',), [('a',)]), (('…',), [('z',)]), (('～',), [('x',)]), (('‧',), [('c',)]),
]
SECOND = ['【', '】', '〈', '〉', '［', '］', '／', '＝', '＿', '｜']

def _candidates(pref, n, free):
    """Preferred keys first, then free keys (or adjacent free pairs) by distance from them."""
    out = [k for k in pref if all(c in free for c in k)]
    r0, i0 = POS[pref[0][0]]
    seqs = []
    for ri, row in enumerate(ROWS):
        for i in range(len(row) - n + 1):
            k = tuple(row[i:i + n])
            if all(c in free for c in k):
                seqs.append((abs(ri - r0) * 1.5 + abs(i - i0), k))
    return out + [k for _, k in sorted(seqs)]

def page(lay):
    tps = {k: v for v, k in panel(lay, ['ㄫ'], True).items()}
    free = {c for r in ROWS for c in r} - DIGITS - set(tps)
    punct = {}
    for syms, pref in ITEMS:
        k = _candidates(pref, len(syms), free)[0]
        for s, c in zip(syms, k): punct[c] = s; free.discard(c)
    return tps, punct, sorted(free, key=lambda c: POS[c])

if __name__ == '__main__':
    var = json.load(open(OUT / 'prefix_variants.json', encoding='utf-8'))
    for m in ('A-P', 'B-P', 'C-P'):
        tps, punct, spare = page(var[m])
        print(m, 'TPS', tps); print('   punct', punct); print('   spare', spare)
