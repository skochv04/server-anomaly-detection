"""Pilot: simple baselines on one SMD machine from TSB-AD-M.

Usage: .venv/Scripts/python pilot.py [csv_path]
"""
import sys
import time

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from TSB_AD.evaluation.metrics import get_metrics
from TSB_AD.model_wrapper import run_Unsupervise_AD
from TSB_AD.utils.slidingWindows import find_length_rank

path = sys.argv[1] if len(sys.argv) > 1 else "data/TSB-AD-M/057_SMD_id_1_Facility_tr_4529_1st_4629.csv"
train_len = int(path.split("_tr_")[1].split("_")[0])

df = pd.read_csv(path).dropna()
data = df.iloc[:, :-1].values.astype(float)
label = df["Label"].astype(int).values

# normalization statistics from the train part only
scaler = StandardScaler().fit(data[:train_len])
data = scaler.transform(data)

sliding_window = find_length_rank(data[:, 0:1], rank=1)
test = slice(train_len, None)
print(f"{path}\npoints={len(data)} metrics={data.shape[1]} train={train_len} "
      f"anomaly_share_test={label[test].mean():.3f} window={sliding_window}")


def last3(x, k=3):
    # squared difference from the mean of the previous k points, averaged over metrics
    prev = pd.DataFrame(x).shift(1).rolling(k).mean().values
    return np.nan_to_num(((x - prev) ** 2).mean(axis=1))


def window_var(x, w):
    # variance in a moving window, averaged over metrics
    return pd.DataFrame(x).rolling(w, min_periods=1).var().fillna(0).values.mean(axis=1)


methods = {
    "IForest": lambda: run_Unsupervise_AD("IForest", data, slidingWindow=sliding_window),
    "Last-3": lambda: last3(data),
    f"Var-{sliding_window}": lambda: window_var(data, sliding_window),
}

rows = []
for name, fn in methods.items():
    t0 = time.time()
    score = np.asarray(fn(), dtype=float)
    elapsed = time.time() - t0
    m = get_metrics(score[test], label[test], slidingWindow=sliding_window)
    rows.append({"method": name, "VUS-PR": m["VUS-PR"], "AUC-PR": m["AUC-PR"],
                 "Standard-F1": m["Standard-F1"], "seconds": elapsed})

print(pd.DataFrame(rows).round(3).to_string(index=False))
