# TPS keyboard layout evaluation and optimization

Code and results for the paper *Corpus-Based Evaluation and Optimization of Taiwanese Phonetic Symbol Keyboard Layouts for Desktop and Mobile Input* (manuscript in preparation, target journal: *Journal of Taiwanese Vernacular* 《台語研究》).

The scripts convert Tâi-lô example sentences from the ChhoeTaigi Database into Taiwanese Phonetic Symbol (TPS, 臺灣方音符號) keystroke sequences, score existing and proposed TPS keyboard layouts with a desktop and mobile cost model, and search for new layouts by simulated annealing.

本儲存庫是論文〈台語方音符號鍵盤排列的語料評估與最佳化〉的程式與結果。程式把 ChhoeTaigi 資料庫中的台羅例句轉成方音按鍵序列，用電腦與手機的打字成本模型評估現有與新設計的方音鍵盤排列，並以模擬退火搜尋新排列。

## Requirements

- Python 3.10 or later (results in the paper: Python 3.13, NumPy 2.5, Matplotlib 3.11)
- `pip install -r requirements.txt`
- git, to download the corpus
- For the figures: the Noto Sans CJK TC font (Bopomofo Extended glyphs, including U+31BB)

## Reproducing the results

Run the scripts in this order from the repository folder:

| Step | Command | Output |
| --- | --- | --- |
| 1 | `python get_data.py` | ChhoeTaigi Database at commit `b33c6a1` in `data/` |
| 2 | `python extract.py` | `out/syl.json`, `out/streams.json` (147,072 syllables) |
| 3 | `python optimize_all.py` | `out/runs/` (72 annealing runs: 24 seeds × 3 configurations, 1,000,000 iterations each; about 8 minutes on 2 cores) |
| 4 | `python evaluate.py` | `out/layouts_proposed.json`, `out/scores.csv` |
| 5 | `python figures_proposed.py` and `python figures_existing.py` | `out/figures/*.png` |
| 6 | `python sensitivity.py`, `python tps_entering_variant.py` and `python input_rules.py` | `out/sensitivity.csv` (Section 3.8); proposed layouts rescored with the Taigi-TPS entering key, and the keys freed and syllables affected by each input rule (Section 5.1) |
| 7 (optional) | `python prefix_variants.py` | `out/prefix_variants.json`, `out/prefix_scores.csv` (prefix-key variants A-P, B-P, C-P, scored with a merged and a separate prefix page; `python prefix_variants.py score` re-scores only) |

The annealing optimizes a bigram approximation of the cost model; step 4 rescores every run with the full model and keeps the best one. The annealing uses fixed seeds, so steps 3 and 4 reproduce the layouts and scores in the paper exactly. Set the environment variable `ITERS=20000` for a quick test run of step 3.

Expected output of step 4 (composite score: Taigi-TPS = 100, lower is better). Taigi-TPS is scored with its own entering key: the rime carrying the matching coda followed by the entering key (ㄤ + entering key for -ak, ㆰ for -ap, ㄢ for -at, the bare rime for -h), with tones 4 and 8 on the same key. The Mandarin-extended keyboard puts Taiwanese tones on F1–F9 and has no phone version, so only its desktop cost is reported (desktop index 122.2).

| Layout | Desktop cost | Phone (s/syllable) | Keys/syllable | Shift or long press | Composite |
| --- | --- | --- | --- | --- | --- |
| Taigi-TPS | 8.06 | 1.202 | 3.22 | 0.0% | 100.0 |
| Wu Shou-Li (Taiwanese-dedicated) | 7.69 | 1.247 | 3.50 | 19.1% | 99.6 |
| Taigi Keyboard (Windows) | 8.22 | 1.290 | 3.52 | 20.5% | 104.6 |
| Wu Shou-Li (Mandarin-extended, desktop only) | 9.85 | — | 3.50 | 19.1% | — |
| Taigi Keyboard (Android) | — | 1.396 | 3.74 | 36.7% | — |
| Layout A (Dachien-preserving) | 7.44 | 1.198 | 3.37 | 0.0% | 96.0 |
| Layout B (hand-split) | 4.26 | 1.022 | 3.37 | 0.0% | 68.9 |
| Layout C (structured hand-split) | 4.76 | 1.060 | 3.37 | 0.0% | 73.6 |
| Unconstrained reference | 4.27 | 1.006 | 3.37 | 0.0% | 68.3 |

## Files

| File | Purpose |
| --- | --- |
| `config.py` | Paths and the corpus commit |
| `get_data.py` | Downloads the ChhoeTaigi Database |
| `extract.py` | Extracts and parses Tâi-lô syllables from the dictionary example sentences |
| `units.py` | Tâi-lô to TPS keystroke-unit conversion |
| `model.py` | Key grid, desktop cost and mobile (Fitts' law) cost model; the phone grid follows the Dachien-style Zhuyin keyboard of Gboard (four aligned rows of ten keys, ㄦ/- right of the space bar) |
| `layouts.py` | Existing layouts: Taigi-TPS, Wu Shou-Li (Taiwanese-dedicated and Mandarin-extended), Taigi Keyboard (Windows, Android) |
| `opt.py` | Simulated-annealing search for one configuration and seed |
| `optimize_all.py` | Runs all configurations and seeds |
| `evaluate.py` | Builds Layout C and scores all layouts |
| `prefix_variants.py` | Variants that move rare symbols to a ` prefix page and re-optimize the freed keys (Layout A-P: fixed, see the docstring) |
| `sensitivity.py` | Sensitivity analysis of the model constants |
| `tps_entering_variant.py` | Proposed layouts rescored with the Taigi-TPS entering key |
| `input_rules.py` | Keys freed and syllables affected by each rule of the input logic |
| `prefix_panel.py` | Key assignment of the prefix panel (merged first page: digit keys keep their digits, variants move down the column; keys of symbols a layout keeps on the main layer are left blank) |
| `symbol_page.py` | First symbol page of each layout: TPS variants, digits and common full-width punctuation on the 41-key grid, plus an extra row |
| `figures_prefix.py`, `figures_prefix_panel.py`, `figures_symbol_page.py` | Figures of the prefix variants and of the prefix panel (`python figures_prefix_panel.py en merged`) |
| `figures_*.py` | Keyboard figures (`python figures_proposed.py zh` for Chinese labels) |
| `out/` | Results: proposed layouts, scores and figures |

The ChhoeTaigi data are not redistributed here; `get_data.py` downloads them from the original repository.

## AI assistance

The code was written and run with the assistance of Claude Opus 5.5 (Anthropic, model identifier `claude-opus-5-5`) under the author's direction, in November 2026. The author checked the symbol mappings and the results and is responsible for the content.

## Citation

Please cite the paper once it is published. Until then, cite this repository.
