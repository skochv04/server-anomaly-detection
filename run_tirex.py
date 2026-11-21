import argparse
import os
import time
from pathlib import Path

os.environ.setdefault("TORCHDYNAMO_DISABLE", "1")

import numpy as np
import torch

from common import evaluate, load_series, sliding_window, smd_files
from tirex2 import TimeseriesType, load_model

parser = argparse.ArgumentParser()
parser.add_argument("--data", default="data/TSB-AD-M")
parser.add_argument("--index", type=int, default=None)
parser.add_argument("--context", type=int, default=512)
parser.add_argument("--horizon", type=int, default=10)
parser.add_argument("--first", type=int, default=64)
parser.add_argument("--batch", type=int, default=32)
parser.add_argument("--max-windows", type=int, default=None)
parser.add_argument("--out", default="scores/tirex2")
args = parser.parse_args()

files = smd_files(args.data)
if args.index is not None:
    files = [files[args.index]]
out_dir = Path(args.out)
out_dir.mkdir(parents=True, exist_ok=True)

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"device={device} {torch.cuda.get_device_name(0) if device == 'cuda' else ''}", flush=True)
model = load_model("NX-AI/TiRex-2", device=device)

for path in files:
    out = out_dir / f"{path.stem}.npy"
    if out.exists() and args.max_windows is None:
        print(f"skip {path.name}", flush=True)
        continue
    raw, data, label, train_len = load_series(path)
    data = data.astype(np.float32)
    starts = list(range(args.first, len(data), args.horizon))[:args.max_windows]
    err = np.full(data.shape, np.nan, dtype=np.float32)

    t0 = time.time()
    for i in range(0, len(starts), args.batch):
        chunk = starts[i:i + args.batch]
        series = [TimeseriesType(target=torch.from_numpy(data[max(0, s - args.context):s].T.copy()),
                                 past_covariates=None, future_covariates=None) for s in chunk]
        forecasts = model.forecast(series, prediction_length=args.horizon, output_type="numpy")
        for s, f in zip(chunk, forecasts):
            end = min(s + args.horizon, len(data))
            err[s:end] = (data[s:end] - f[:, 4, :end - s].T) ** 2
    elapsed = time.time() - t0

    points = int((~np.isnan(err[:, 0])).sum())
    print(f"{path.name} windows={len(starts)} points={points} seconds={elapsed:.1f} "
          f"per_1000_points={1000 * elapsed / points:.2f}", flush=True)
    if args.max_windows is None:
        np.save(out, err)
        vus, f1 = evaluate(err.mean(axis=1), label, train_len, sliding_window(data))
        print(f"{path.name[:3]} TiRex-2 VUS-PR={vus:.3f} Standard-F1={f1:.3f}", flush=True)
