"""Run the annealing search for Layouts A, B and the unconstrained reference.
Seeds 1-6, 250,000 iterations each (as in the paper). Results go to out/runs/.
Set ITERS=20000 in the environment for a quick test run."""
import os, json, subprocess, sys
from multiprocessing import Pool
from config import OUT, ROOT
ITERS = int(os.environ.get('ITERS', 250000))
RUNS = OUT / 'runs'; RUNS.mkdir(exist_ok=True)
def job(arg):
    mode, seed = arg
    out = subprocess.run([sys.executable, str(ROOT / 'opt.py'), mode, str(seed), str(ITERS)],
                         capture_output=True, text=True, check=True).stdout
    (RUNS / f'{mode}_{seed}.json').write_text(out, encoding='utf-8')
    return mode, seed, json.loads(out)['cost']
if __name__ == '__main__':
    jobs = [(m, s) for m in ('A', 'B', 'free') for s in range(1, 7)]
    with Pool() as p:
        for m, s, c in p.imap_unordered(job, jobs):
            print(f'{m} seed {s}: cost {c:.4f}')
