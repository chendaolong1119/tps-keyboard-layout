"""Draw the proposed Taiwanese page of the ` prefix panel for Layouts A-P, B-P, C-P.
Each variant sits on the key of its related main-layer symbol (shown small in grey).
Usage: python figures_prefix_panel.py [en|zh]"""
import json, sys, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams['font.family'] = ['Noto Sans CJK TC', 'DejaVu Sans']
from model import ROWS
from config import OUT
# variant -> related main-layer symbol
REL = {'ㄫ': 'ㄍ', 'ㆱ': 'ㆰ', 'ˇ': 'ˋ', 'ˆ': 'ˊ', 'ㆨ': 'ㄨ', 'ㄛ': 'ㆦ', 'ㄝ': 'ㆤ',
       'ㄬ': 'ㄋ', 'dd': 'ㄉ', 'eer': 'ㄜ'}
RESERVED = {'u': 'U+', 'b': 'Big5'}      # Microsoft Bopomofo: `U = Unicode, `B = Big5
LANG = sys.argv[1] if len(sys.argv) > 1 else 'en'
T = {'en': dict(tabs=['General', 'Taiwanese', 'Math', 'Special'], nas='nas',
                title='{}: Taiwanese page of the ` prefix panel  (` → Tab → key)',
                note='Large: symbol entered;  small grey: main-layer symbol on the same key;  hatched: left free for Microsoft Bopomofo (`U Unicode, `B Big5)',
                names={'A-P': 'Layout A-P', 'B-P': 'Layout B-P', 'C-P': 'Layout C-P'}),
     'zh': dict(tabs=['一般', '台語', '數學', '特殊'], nas='鼻',
                title='{}：‵ 前置面板的「台語」頁（‵ → Tab → 鍵）',
                note='大字＝輸入的符號；灰色小字＝同一鍵主層的符號；斜線＝保留給微軟注音（‵U Unicode 碼、‵B Big5 碼）',
                names={'A-P': '方案甲-P', 'B-P': '方案乙-P', 'C-P': '方案丙-P'})}[LANG]

def draw(lay, fn, name):
    inv = {c: u for u, c in lay.items()}
    var = {}
    for v, r in REL.items():
        k = lay.get(r)
        if k:
            assert k not in var, (name, k, var.get(k), v)
            var[k] = v
    fig, ax = plt.subplots(figsize=(11.5, 5.4)); ax.set_xlim(-0.1, 11.3); ax.set_ylim(-0.6, 5.9); ax.axis('off')
    # tabs
    for i, t in enumerate(T['tabs']):
        on = i == 1
        ax.add_patch(FancyBboxPatch((0.05 + i * 1.6, 5.05), 1.5, 0.55, boxstyle='round,pad=0,rounding_size=0.1',
                                    fc='#5b4a9e' if on else '#ececec', ec='#888', lw=0.8))
        ax.text(0.8 + i * 1.6, 5.32, t, ha='center', va='center', fontsize=11, color='white' if on else '#555',
                weight='bold' if on else 'normal')
    offs = [0, 0.5, 0.75, 1.25]
    for ri, r in enumerate(ROWS):
        for i, c in enumerate(r):
            x = offs[ri] + i; y = 4 - ri
            v = var.get(c); res = c in RESERVED
            ax.add_patch(FancyBboxPatch((x + 0.05, y + 0.05), 0.9, 0.9, boxstyle='round,pad=0.0,rounding_size=0.12',
                                        fc='#efe9fb' if v else '#f7f7f7', ec='#888', lw=0.8,
                                        hatch='///' if res else None))
            ax.text(x + 0.13, y + 0.82, c.upper(), fontsize=8, color='#777', va='top')
            u = inv.get(c)
            if u: ax.text(x + 0.87, y + 0.12, T['nas'] if u == 'N' else u, fontsize=9, color='#999', ha='right', va='bottom')
            if v:
                big = v not in ('dd', 'eer')
                ax.text(x + 0.5, y + 0.45, v, fontsize=20 if big else 13, ha='center', va='center', color='#4a2f8f')
            if res: ax.text(x + 0.5, y + 0.45, RESERVED[c], fontsize=8, ha='center', va='center', color='#a33',
                            bbox=dict(fc='white', ec='none', pad=1))
    ax.text(5.55, -0.35, T['note'], fontsize=9, ha='center', va='center', color='#555')
    ax.set_title(T['title'].format(T['names'][name]), fontsize=12)
    fig.savefig(fn, dpi=160, bbox_inches='tight'); plt.close(fig)

if __name__ == '__main__':
    var = json.load(open(OUT / 'prefix_variants.json', encoding='utf-8'))
    for m in ('A-P', 'B-P', 'C-P'):
        draw(var[m], OUT / 'figures' / f"panel_{m.replace('-', '_')}{'' if LANG == 'en' else '_zh'}.png", m)
