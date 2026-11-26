"""Draw the first symbol page (desktop ` then key; phone symbol key then key) for A-P, B-P, C-P,
with the extra row used on the phone (second page on the desktop).
Usage: python figures_symbol_page.py [en|zh]"""
import json, sys, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams['font.family'] = ['Noto Sans CJK TC', 'DejaVu Sans']
from model import ROWS
from config import OUT
from symbol_page import page, SECOND
LANG = sys.argv[1] if len(sys.argv) > 1 else 'en'
T = {'en': dict(nas='nas', names={'A-P': 'Layout A-P', 'B-P': 'Layout B-P', 'C-P': 'Layout C-P'},
                title='{}: first symbol page (desktop ` → key; phone symbol key → key)',
                extra='Extra row: fifth row on the phone, second page on the desktop',
                note='Purple: TPS symbol;  green: full-width punctuation;  black: digit;  small grey: main-layer symbol;  blank: spare'),
     'zh': dict(nas='鼻', names={'A-P': '方案甲-P', 'B-P': '方案乙-P', 'C-P': '方案丙-P'},
                title='{}：符號第一頁（電腦 ‵ → 鍵；手機 符號鍵 → 鍵）',
                extra='延伸列：手機第 5 列；電腦第 2 頁',
                note='紫＝方音符號；綠＝全形標點；黑＝數字；灰色小字＝主層符號；空白＝可再放其他符號')}[LANG]

def key(ax, x, y, fc):
    ax.add_patch(FancyBboxPatch((x + .05, y + .05), .9, .9, boxstyle='round,pad=0.0,rounding_size=0.12', fc=fc, ec='#888', lw=.8))

def draw(lay, fn, name):
    tps, punct, spare = page(lay)
    inv = {c: u for u, c in lay.items()}
    fig, ax = plt.subplots(figsize=(11.5, 6.4)); ax.set_xlim(-0.1, 11.3); ax.set_ylim(-1.9, 5.2); ax.axis('off')
    offs = [0, 0.5, 0.75, 1.25]
    for ri, r in enumerate(ROWS):
        for i, c in enumerate(r):
            x = offs[ri] + i; y = 4 - ri
            v, p = tps.get(c), punct.get(c)
            key(ax, x, y, '#efe9fb' if v else '#e3f0e3' if p else '#f7f7f7')
            ax.text(x + .13, y + .82, c.upper(), fontsize=8, color='#777', va='top')
            u = inv.get(c)
            if u: ax.text(x + .87, y + .12, T['nas'] if u == 'N' else u, fontsize=9, color='#999', ha='right', va='bottom')
            if v: ax.text(x + .5, y + .45, v, fontsize=20 if v not in ('dd', 'eer') else 13, ha='center', va='center', color='#4a2f8f')
            elif p: ax.text(x + .5, y + .45, p, fontsize=18 if len(p) == 1 else 14, ha='center', va='center', color='#1d6b2a')
            elif c.isdigit(): ax.text(x + .5, y + .45, c, fontsize=16, ha='center', va='center', color='#222')
    ax.text(0.05, -0.35, T['extra'], fontsize=10, va='center', color='#555')
    for i, s in enumerate(SECOND):
        key(ax, 0.5 + i, -1.6, '#e3f0e3')
        ax.text(1.0 + i, -1.15, s, fontsize=16, ha='center', va='center', color='#1d6b2a')
    ax.plot([-0.05, 11.25], [-0.05, -0.05], color='#bbb', lw=0.8, ls='--')
    ax.set_title(T['title'].format(T['names'][name]), fontsize=12)
    fig.text(0.5, 0.01, T['note'], fontsize=9, ha='center', color='#555')
    fig.savefig(fn, dpi=160, bbox_inches='tight'); plt.close(fig)

if __name__ == '__main__':
    var = json.load(open(OUT / 'prefix_variants.json', encoding='utf-8'))
    for m in ('A-P', 'B-P', 'C-P'):
        draw(var[m], OUT / 'figures' / f"symbols_{m.replace('-', '_')}{'' if LANG == 'en' else '_zh'}.png", m)
