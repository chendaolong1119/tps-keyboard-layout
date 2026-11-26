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
| 3 | `python optimize_all.py` | `out/runs/` (18 annealing runs, about 1 minute on 2 cores) |
| 4 | `python evaluate.py` | `out/layouts_proposed.json`, `out/scores.csv` |
| 5 | `python figures_proposed.py` and `python figures_existing.py` | `out/figures/*.png` |
| 6 (optional) | `python prefix_variants.py` | `out/prefix_variants.json`, `out/prefix_scores.csv` (prefix-key variants A-P, B-P, C-P) |

The annealing uses fixed seeds, so steps 3 and 4 reproduce the layouts and scores in the paper exactly. Set the environment variable `ITERS=20000` for a quick test run of step 3.

Expected output of step 4 (composite score: Taigi-TPS = 100, lower is better). The Mandarin-extended keyboard puts Taiwanese tones on F1–F9 and has no phone version, so only its desktop cost is reported (desktop index 124.2).

| Layout | Desktop cost | Phone (s/syllable) | Keys/syllable | Shift or long press | Composite |
| --- | --- | --- | --- | --- | --- |
| Taigi-TPS | 7.93 | 1.244 | 3.37 | 0.0% | 100.0 |
| Wu Shou-li (Taiwanese-dedicated) | 7.69 | 1.274 | 3.50 | 19.1% | 99.6 |
| Taigi Keyboard (Windows) | 8.22 | 1.295 | 3.52 | 20.5% | 103.8 |
| Wu Shou-li (Mandarin-extended, desktop only) | 9.85 | — | 3.50 | 19.1% | — |
| Taigi Keyboard (Android) | — | 1.402 | 3.74 | 36.7% | — |
| Layout A (Dachien-preserving) | 7.19 | 1.199 | 3.37 | 0.0% | 93.5 |
| Layout B (hand-split) | 4.26 | 1.041 | 3.37 | 0.0% | 68.7 |
| Layout C (structured hand-split) | 4.76 | 1.073 | 3.37 | 0.0% | 73.1 |
| Unconstrained reference | 4.25 | 1.036 | 3.37 | 0.0% | 68.4 |

## Files

| File | Purpose |
| --- | --- |
| `config.py` | Paths and the corpus commit |
| `get_data.py` | Downloads the ChhoeTaigi Database |
| `extract.py` | Extracts and parses Tâi-lô syllables from the dictionary example sentences |
| `units.py` | Tâi-lô to TPS keystroke-unit conversion |
| `model.py` | Key grid, desktop cost and mobile (Fitts' law) cost model |
| `layouts.py` | Existing layouts: Taigi-TPS, Wu Shou-li (Taiwanese-dedicated and Mandarin-extended), Taigi Keyboard (Windows, Android) |
| `opt.py` | Simulated-annealing search for one configuration and seed |
| `optimize_all.py` | Runs all configurations and seeds |
| `evaluate.py` | Builds Layout C and scores all layouts |
| `prefix_variants.py` | Variants that move rare symbols to a ` prefix page and re-optimize the freed keys |
| `figures_*.py` | Keyboard figures |
| `out/` | Results: proposed layouts, scores and figures |

The ChhoeTaigi data are not redistributed here; `get_data.py` downloads them from the original repository.

## AI assistance

The code was written and run with the assistance of Claude Opus 5.5 (Anthropic, model identifier `claude-opus-5-5`) under the author's direction, in November 2026. The author checked the symbol mappings and the results and is responsible for the content.

## Citation

Please cite the paper once it is published. Until then, cite this repository.
