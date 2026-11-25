import argparse
import time
from pathlib import Path

import numpy as np
import torch

from common import evaluate, load_series, sliding_window, smd_files
from toto2 import Toto2Model

parser = argparse.ArgumentParser()
parser.add_argument("--data", default="data/TSB-AD-M")
parser.add_argument("--index", type=int, default=None)
parser.add_argument("--model", default="Datadog/Toto-2.0-313m")
parser.add_argument("--context", type=int, default=512)
parser.add_argument("--horizon", type=int, default=10)
parser.add_argument("--first", type=int, default=64)
parser.add_argument("--batch", type=int, default=32)
parser.add_argument("--max-windows", type=int, default=None)
parser.add_argument("--out", default="scores/toto")
args = parser.parse_args()

files = smd_files(args.data)
if args.index is not None:
    files = [files[args.index]]
out_dir = Path(args.out)
out_dir.mkdir(parents=True, exist_ok=True)

device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"device={device} {torch.cuda.get_device_name(0) if device == 'cuda' else ''}", flush=True)
model = Toto2Model.from_pretrained(args.model, map_location=device).to(device).eval()
patch = model.config.patch_size
median = model.output_head.knots.index(0.5)
print(f"model={args.model} parameters={sum(p.numel() for p in model.parameters()):,} "
      f"patch_size={patch} quantiles={model.output_head.knots}", flush=True)
assert args.context % patch == 0, f"--context must be a multiple of {patch}"

for path in files:
    out = out_dir / f"{path.stem}.npy"
    if out.exists() and args.max_windows is None:
        print(f"skip {path.name}", flush=True)
        continue
    raw, data, label, train_len = load_series(path)
    data = data.astype(np.float32)
    n_var = data.shape[1]
    starts = list(range(args.first, len(data), args.horizon))[:args.max_windows]
    err = np.full(data.shape, np.nan, dtype=np.float32)

    t0 = time.time()
    for i in range(0, len(starts), args.batch):
        chunk = starts[i:i + args.batch]
        # Short histories are left-padded and masked as not observed.
        target = np.zeros((len(chunk), n_var, args.context), dtype=np.float32)
        mask = np.zeros(target.shape, dtype=bool)
        for j, s in enumerate(chunk):
            ctx = data[max(0, s - args.context):s].T
            target[j, :, -ctx.shape[1]:] = ctx
            mask[j, :, -ctx.shape[1]:] = True
        inputs = {"target": torch.from_numpy(target).to(device),
                  "target_mask": torch.from_numpy(mask).to(device),
                  "series_ids": torch.zeros(len(chunk), n_var, dtype=torch.long, device=device)}
        with torch.inference_mode():
            q = model.forecast(inputs, horizon=args.horizon, decode_block_size=None,
                               has_missing_values=not mask.all())
        forecasts = q[median].float().cpu().numpy()
        for s, f in zip(chunk, forecasts):
            end = min(s + args.horizon, len(data))
            err[s:end] = (data[s:end] - f[:, :end - s].T) ** 2
    elapsed = time.time() - t0

    points = int((~np.isnan(err[:, 0])).sum())
    print(f"{path.name} windows={len(starts)} points={points} seconds={elapsed:.1f} "
          f"per_1000_points={1000 * elapsed / points:.2f}", flush=True)
    if args.max_windows is None:
        np.save(out, err)
        vus, f1 = evaluate(err.mean(axis=1), label, train_len, sliding_window(data))
        print(f"{path.name[:3]} Toto VUS-PR={vus:.3f} Standard-F1={f1:.3f}", flush=True)
