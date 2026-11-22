import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from common import evaluate, load_series, sliding_window, smd_files

parser = argparse.ArgumentParser()
parser.add_argument("method")
parser.add_argument("--data", default="data/TSB-AD-M")
parser.add_argument("--scores", default=None)
parser.add_argument("--out", default=None)
args = parser.parse_args()

score_dir = Path(args.scores or f"scores/{args.method.lower()}")
out = Path(args.out or f"results/{args.method.lower()}.csv")

rows = []
for path in smd_files(args.data):
    score_file = score_dir / f"{path.stem}.npy"
    if not score_file.exists():
        continue
    raw, data, label, train_len = load_series(path)
    err = np.load(score_file)
    vus, f1 = evaluate(err.mean(axis=1), label, train_len, sliding_window(data))
    rows.append({"server": path.name[:3], "method": args.method, "seed": 0, "train_len": train_len,
                 "VUS-PR": round(vus, 4), "Standard-F1": round(f1, 4)})
    print(f"{path.name[:3]} {args.method} VUS-PR={vus:.3f}", flush=True)

table = pd.DataFrame(rows)
table.to_csv(out, index=False)
print(f"{len(table)} servers, mean VUS-PR={table['VUS-PR'].mean():.3f} -> {out}")
