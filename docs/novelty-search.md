# Novelty search: TiRex / Toto + anomaly detection

Item 1 for consultation 1 (23.10.2026). Searched on 21.10.2026: arXiv, Google Scholar (by hand), OpenAlex, web search, GitHub.

## Short answer

Our exact setup has not been done. Close works exist, so the novelty claim is narrowed:

- **TiRex-2**: not used for anomaly detection anywhere.
- **First TiRex**: used once (IBM), on other data.
- **Toto / Toto 2.0**: used for anomalies in drilling, spacecraft and one storage cluster, but never compared with per-server LSTM/GRU and without cold start.

## Closest papers

| Paper | What they did | Difference from us |
|---|---|---|
| Martinez Gil et al. (IBM), 04.2026 · [arXiv](https://arxiv.org/abs/2604.20122) | First TiRex, Chronos-Bolt, TTM; forecast error + label-free threshold | No SMD, no TiRex-2/Toto, no LSTM/GRU |
| Yum, 2026, technical report · [PDF](https://seoyoonyum.github.io/assets/pdf/papers/tsfm_ad_technical_report.pdf) | **Toto 2.0** (313M) on a Ceph storage cluster and a video pipeline, plus TSB-AD-M | **Closest for Toto.** No TiRex-2, no LSTM/GRU, no cold start, not peer-reviewed. On TSB-AD-M a simple baseline beat Toto (VUS-PR 0.29 vs 0.14) |
| Sengupta et al., ICML 2026 workshop · [page](https://icml.cc/virtual/2026/71509) | First Toto and Chronos-2 on oil and gas drilling signals | Not server data; no TiRex, no LSTM |
| Olive et al., CVPR 2026 workshop (AI4Space) · [list](https://openaccess.thecvf.com/CVPR2026_workshops/AI4Space) | Forecasting foundation models incl. Toto on spacecraft telemetry | Not server data. Seen only in a Scholar snippet; full text not opened |
| Zhu et al., ICLR 2026 · [page](https://mlanthology.org/iclr/2026/zhu2026iclr-foundation/) | Foundation models are not better than one-line rules (e.g. moving-window variance) | No TiRex/Toto. Warning: we should add simple baselines too |
| Varverakis et al., Future Internet 2026 · [MDPI](https://www.mdpi.com/1999-5903/18/10/550) | TiRex forecasts barely change when spikes are injected | Forecasting only, not anomaly detection |
| TAB benchmark, PVLDB 2025 · [PDF](https://www.vldb.org/pvldb/vol18/p2775-hu.pdf) | Older foundation models on SMD and other data | No TiRex/Toto |

Also seen, but not relevant: xLSTMAD, F2A, STAR, RATFM, RAMSAD, Schausberger 2026 (out-of-distribution detection), and Toto papers on forecasting or question answering (Netburst, ARFBench, TelecomTS).

## Novelty statement

> To our knowledge, **TiRex-2** has not yet been evaluated for anomaly detection, and nobody has compared zero-shot **TiRex-2** and **Toto 2.0** with LSTM/GRU trained separately for each server on server metrics (SMD), taking cold start and false alarms into account. Earlier works tested older or single models on other data: the first TiRex (IBM, 2026), Toto on drilling and spacecraft data (2026), and Toto 2.0 on one storage cluster (Yum, 2026).

## What this means for the plan

- Add two one-line baselines: moving-window variance and squared difference.
- Yum (2026) found that Toto 2.0 loses to a simple baseline on TSB-AD-M. That is a risk for us, but it makes the question more interesting.

## Limitations

- Google Scholar ("Since 2025"): all 10 pages (102 results) checked by hand for `"TiRex" anomaly detection`, and several pages for `"Toto" Datadog anomaly detection`. After the papers above, the hits only cite TiRex/Toto as forecasters, are surveys, or are unrelated ("in-toto" software security).
- Some papers were read only from their summary pages.
- Repeat the search before submission (December).
