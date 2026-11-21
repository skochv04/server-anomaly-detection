from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

np.Inf = np.inf

from TSB_AD.evaluation.metrics import get_metrics
from TSB_AD.utils.slidingWindows import find_length_rank


def smd_files(data_dir="data/TSB-AD-M"):
    return sorted(Path(data_dir).glob("*_SMD_*.csv"))


def load_series(path):
    path = Path(path)
    train_len = int(path.name.split("_tr_")[1].split("_")[0])
    df = pd.read_csv(path).dropna()
    raw = df.iloc[:, :-1].values.astype(float)
    label = df["Label"].astype(int).values
    data = StandardScaler().fit(raw[:train_len]).transform(raw)
    return raw, data, label, train_len


def sliding_window(data):
    return find_length_rank(data[:, 0:1], rank=1)


def evaluate(score, label, train_len, window):
    test_score = np.nan_to_num(np.asarray(score, dtype=float)[train_len:], nan=0.0)
    m = get_metrics(test_score, label[train_len:], slidingWindow=window)
    return m["VUS-PR"], m["Standard-F1"]
