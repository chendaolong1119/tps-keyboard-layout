"""Key assignment of the ` prefix panel.

Every variant sits on the key of a related main-layer symbol. Two designs:
  separate : TPS symbols on their own page (` Tab key); any key may be used.
  merged   : TPS symbols share the first page with full-width digits and punctuation (` key).
             The digit keys keep their full-width digits, so a variant whose related symbol is
             on a digit key moves straight down the same column to the first free letter key.
             (Bottom-row collisions, which occur only in the P+ variants, take the nearest free key.)
             U and B stay free for the Unicode and Big5 code entry of the Microsoft Bopomofo IME.
"""
from model import ROWS

REL = {'ㄫ': 'ㄍ', 'ㆡ': 'ㄗ', 'ㆭ': 'ㄥ', 'ㆰ': 'ㄢ', 'ㆱ': 'ㆰ', 'ˇ': 'ˋ', 'ˆ': 'ˊ',
       'ㆨ': 'ㄨ', 'ㄛ': 'ㆦ', 'ㄝ': 'ㆤ', 'ㄬ': 'ㄋ', 'dd': 'ㄉ', 'eer': 'ㄜ'}
EXTRA = ['ㆨ', 'ㄛ', 'ㄝ', 'ㄬ', 'dd', 'eer']     # not in the corpus; shown on the panel only
RESERVED = {'u', 'b'}
DIGITS = set('1234567890')
POS = {c: (ri, i) for ri, r in enumerate(ROWS) for i, c in enumerate(r)}

def related_key(lay, v):
    r = REL[v]
    return lay.get(r) or lay.get(REL.get(r, ''))

def panel(lay, moved, merged):
    """Return {variant: key} for the moved units, ㆱ ˇ ˆ, and the panel-only extras."""
    vs = list(moved) + [u for u in ('ㆱ', 'ˇ', 'ˆ') if u not in moved] + EXTRA
    if not merged:
        return {v: related_key(lay, v) for v in vs}
    out, taken = {}, set(RESERVED)
    first = [v for v in vs if related_key(lay, v) not in DIGITS]
    later = [v for v in vs if related_key(lay, v) in DIGITS]
    for v in first + later:
        k = related_key(lay, v)
        if k in DIGITS or k in taken:
            ri, i = POS[k]
            k = None
            for r2 in range(ri + 1, len(ROWS)):
                if i < len(ROWS[r2]) and ROWS[r2][i] not in taken | DIGITS:
                    k = ROWS[r2][i]; break
            if k is None:   # bottom row: nearest free key in the same row, then in the row above
                for r2 in (ri, ri - 1):
                    free = [c for c in ROWS[r2] if c not in taken | DIGITS]
                    if free:
                        k = min(free, key=lambda c: abs(POS[c][1] - i)); break
            assert k, (v, related_key(lay, v))
        out[v] = k; taken.add(k)
    return out
