"""Download the ChhoeTaigi Database at the exact commit used in the paper (needs git)."""
import subprocess
from config import ROOT, CHHOETAIGI_COMMIT
d = ROOT / 'data' / 'ChhoeTaigiDatabase'
if not d.exists():
    d.parent.mkdir(exist_ok=True)
    subprocess.run(['git', 'clone', 'https://github.com/ChhoeTaigi/ChhoeTaigiDatabase.git', str(d)], check=True)
subprocess.run(['git', '-C', str(d), 'checkout', CHHOETAIGI_COMMIT], check=True)
print('ChhoeTaigi data ready at', d)
