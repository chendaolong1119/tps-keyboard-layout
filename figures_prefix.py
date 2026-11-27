"""Draw the prefix-key variants (A-P, B-P, C-P): main layer plus the symbols
reached through the ` prefix page, shown in purple at the lower right of the key
given by prefix_panel.py (merged symbol page). Usage: python figures_prefix.py [en|zh]"""
import json, sys, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
plt.rcParams['font.family'] = ['Noto Sans CJK TC', 'DejaVu Sans']
from model import ROWS
from config import OUT
INITIALS = list('ㄅㄆㄇㆠㄉㄊㄋㄌㄍㄎㄫㆣㄏㄗㄘㄙㆡ')
AUTO = {'ㄅ': 'ㆴ', 'ㄉ': 'ㆵ', 'ㄍ': 'ㆻ', 'ㄏ': 'ㆷ'}
TONES = 'ˋ˪ˊ˫˙'
COL = {'ini': '#dbe9f6', 'rime': '#fbe3cf', 'tone': '#e2f0d9', 'nas': '#eadcf2', 'none': '#f2f2f2'}
LANG = sys.argv[1] if len(sys.argv) > 1 else 'en'
T = {'en': dict(nas='nas', space='Space = tones 1 and 4',
                leg=['Initial', 'Rime', 'Tone', 'Nasalization'],
                note=' (red = auto-converted; purple = via ` prefix page)',
                titles={'A-P': 'Layout A-P: Dachien-preserving with prefix page',
                        'B-P': 'Layout B-P: hand-split with prefix page',
                        'C-P': 'Layout C-P: structured hand-split with prefix page'}),
     'zh': dict(nas='鼻', space='空白鍵＝第 1、4 聲', leg=['聲母', '韻母', '聲調', '鼻化'],
                note='（紅字＝自動轉換；紫字＝‵ 前置頁）',
                titles={'A-P': '方案甲-P：大千保留型＋前置頁',
                        'B-P': '方案乙-P：左右分區型＋前置頁',
                        'C-P': '方案丙-P：結構化分區型＋前置頁'})}[LANG]

def cat(u):
    if u is None: return 'none'
    if u in INITIALS: return 'ini'
    if u in TONES: return 'tone'
    if u == 'N': return 'nas'
    return 'rime'

def draw(lay, fn, title):
    inv = {c: u for u, c in lay.items()}
    from prefix_panel import panel
    pre = {}
    for p, k in panel(lay, ['ㄫ'], True).items():   # merged symbol page (prefix_panel.py)
        pre[k] = pre.get(k, '') + p
    fig, ax = plt.subplots(figsize=(11.5, 4.6)); ax.set_xlim(-0.1, 11.3); ax.set_ylim(-0.3, 5.3); ax.axis('off')
    offs = [0, 0.5, 0.75, 1.25]
    for ri, r in enumerate(ROWS):
        for i, c in enumerate(r):
            x = offs[ri] + i; y = 4 - ri; u = inv.get(c)
            ax.add_patch(FancyBboxPatch((x + 0.05, y + 0.05), 0.9, 0.9, boxstyle='round,pad=0.0,rounding_size=0.12',
                                        fc=COL[cat(u)], ec='#888', lw=0.8))
            ax.text(x + 0.13, y + 0.82, c.upper(), fontsize=8, color='#777', va='top')
            if u: ax.text(x + 0.5, y + 0.42, T['nas'] if u == 'N' else u, fontsize=20 if u != 'N' else 15, ha='center', va='center')
            if u in AUTO: ax.text(x + 0.85, y + 0.82, AUTO[u], fontsize=10, color='#c0392b', ha='right', va='top')
            if c in pre: ax.text(x + 0.87, y + 0.12, pre[c], fontsize=10, color='#7d3c98', ha='right', va='bottom')
    ax.add_patch(FancyBboxPatch((3.3, -0.2), 4.5, 0.75, boxstyle='round,pad=0.0,rounding_size=0.12', fc=COL['tone'], ec='#888', lw=0.8))
    ax.text(5.55, 0.17, T['space'], fontsize=11, ha='center', va='center')
    for k, (lab, cc) in enumerate(zip(T['leg'], ['ini', 'rime', 'tone', 'nas'])):
        ax.add_patch(FancyBboxPatch((8.4 + k * 0.72, 0.05), 0.22, 0.22, boxstyle='square,pad=0', fc=COL[cc], ec='#888'))
        ax.text(8.68 + k * 0.72, 0.16, lab, fontsize=9, va='center')
    ax.set_title(title + T['note'], fontsize=12)
    fig.savefig(fn, dpi=160, bbox_inches='tight'); plt.close(fig)

if __name__ == '__main__':
    var = json.load(open(OUT / 'prefix_variants.json', encoding='utf-8'))
    d = OUT / 'figures'; d.mkdir(exist_ok=True)
    for m in ('A-P', 'B-P', 'C-P'):
        draw(var[m], d / f"layout_{m.replace('-', '_')}{'' if LANG == 'en' else '_zh'}.png", T['titles'][m])
