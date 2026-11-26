"""Paths shared by all scripts."""
from pathlib import Path
ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data' / 'ChhoeTaigiDatabase' / 'ChhoeTaigiDatabase'
OUT = ROOT / 'out'
OUT.mkdir(exist_ok=True)
(OUT / 'figures').mkdir(exist_ok=True)
CHHOETAIGI_COMMIT = 'b33c6a1fcc2d11a2962e76b6055d528d11677c3b'
