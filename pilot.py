import sys
import time

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

from TSB_AD.evaluation.metrics import get_metrics
from TSB_AD.models.IForest import IForest
from TSB_AD.utils.slidingWindows import find_length_rank

SEEDS = range(5)

path = sys.argv[1] if len(sys.argv) > 1 else "data/TSB-AD-M/057_SMD_id_1_Facility_tr_4529_1st_4629.csv"
train_len = int(path.split("_tr_")[1].split("_")[0])

df = pd.read_csv(path).dropna()
raw = df.iloc[:, :-1].values.astype(float)
label = df["Label"].astype(int).values

data = StandardScaler().fit(raw[:train_len]).transform(raw)

sliding_window = find_length_rank(data[:, 0:1], rank=1)
test = slice(train_len, None)
print(f"{path}\npoints={len(data)} metrics={data.shape[1]} train={train_len} "
      f"anomaly_share_test={label[test].mean():.3f} window={sliding_window}")


def last3(x, k=3):
    prev = pd.DataFrame(x).shift(1).rolling(k).mean().values
    return np.nan_to_num(((x - prev) ** 2).mean(axis=1))


def window_var(x, w):
    return pd.DataFrame(x).rolling(w, min_periods=1).var().fillna(0).values.mean(axis=1)


def iforest(seed):
    clf = IForest(slidingWindow=sliding_window, n_estimators=100, max_features=1.0,
                  random_state=seed, n_jobs=1)
    clf.fit(raw)
    return clf.decision_scores_.ravel()


methods = {
    "IForest": [lambda s=s: iforest(s) for s in SEEDS],
    "Last-3": [lambda: last3(data)],
    f"Var-{sliding_window}": [lambda: window_var(data, sliding_window)],
}

rows = []
for name, runs in methods.items():
    results = []
    for fn in runs:
        t0 = time.time()
        score = np.asarray(fn(), dtype=float)
        elapsed = time.time() - t0
        m = get_metrics(score[test], label[test], slidingWindow=sliding_window)
        results.append((m["VUS-PR"], m["Standard-F1"], elapsed))
    r = np.array(results)
    rows.append({"method": name, "runs": len(r),
                 "VUS-PR": r[:, 0].mean(), "VUS-PR std": r[:, 0].std(),
                 "Standard-F1": r[:, 1].mean(), "seconds": r[:, 2].mean()})

print(pd.DataFrame(rows).round(3).to_string(index=False))
