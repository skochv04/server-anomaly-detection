import argparse
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

from common import evaluate, load_series, sliding_window, smd_files
from TSB_AD.models.IForest import IForest
from TSB_AD.models.LSTMAD import LSTMAD

parser = argparse.ArgumentParser()
parser.add_argument("--data", default="data/TSB-AD-M")
parser.add_argument("--if-seeds", type=int, default=5)
parser.add_argument("--lstm-seeds", type=int, default=3)
parser.add_argument("--scores", default="scores")
parser.add_argument("--out", default="results/local.csv")
args = parser.parse_args()

score_dir = Path(args.scores)
score_dir.mkdir(parents=True, exist_ok=True)
out = Path(args.out)
out.parent.mkdir(parents=True, exist_ok=True)
done = pd.read_csv(out) if out.exists() else pd.DataFrame(columns=["server", "method", "seed"])
done_keys = set(zip(done["server"].astype(str).str.zfill(3), done["method"], done["seed"]))
rows = done.to_dict("records")


def last3(data, k=3):
    prev = pd.DataFrame(data).shift(1).rolling(k).mean().values
    return np.nan_to_num(((data - prev) ** 2).mean(axis=1))


def window_var(data, w):
    return pd.DataFrame(data).rolling(w, min_periods=1).var().fillna(0).values.mean(axis=1)


def iforest(raw, w, seed):
    clf = IForest(slidingWindow=w, n_estimators=100, max_features=1.0, random_state=seed, n_jobs=1)
    clf.fit(raw)
    return clf.decision_scores_.ravel()


def lstm(data, train_len, seed):
    torch.manual_seed(seed)
    np.random.seed(seed)
    clf = LSTMAD(window_size=100, pred_len=1, lr=0.0008, feats=data.shape[1], batch_size=128)
    clf.fit(data[:train_len])
    return clf.decision_function(data)


for path in smd_files(args.data):
    server = path.name[:3]
    raw, data, label, train_len = load_series(path)
    w = sliding_window(data)
    runs = [("Last-3", 0, lambda: last3(data)),
            ("Var", 0, lambda: window_var(data, w))]
    runs += [("IForest", s, lambda s=s: iforest(raw, w, s)) for s in range(args.if_seeds)]
    runs += [("LSTM", s, lambda s=s: lstm(data, train_len, s)) for s in range(args.lstm_seeds)]
    for method, seed, fn in runs:
        if (server, method, seed) in done_keys:
            continue
        t0 = time.time()
        score = np.asarray(fn(), dtype=float).ravel()
        seconds = time.time() - t0
        vus, f1 = evaluate(score, label, train_len, w)
        np.save(score_dir / f"{path.stem}_{method}_seed{seed}.npy", score.astype(np.float32))
        rows.append({"server": server, "method": method, "seed": seed, "train_len": train_len,
                     "VUS-PR": round(vus, 4), "Standard-F1": round(f1, 4), "seconds": round(seconds, 1)})
        pd.DataFrame(rows).to_csv(out, index=False)
        print(f"{server} {method} seed={seed} VUS-PR={vus:.3f} seconds={seconds:.1f}", flush=True)

table = pd.DataFrame(rows)
per_server = table.groupby(["method", "server"])["VUS-PR"].mean().reset_index()
print(per_server.groupby("method")["VUS-PR"].agg(["mean", "median", "count"]).round(3).to_string())
