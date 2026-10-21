# Novelty search: has anyone evaluated TiRex / Toto for anomaly detection?

Item 1 of the plan for consultation 1 (23.10.2026). Search done on 21.10.2026 (web search, arXiv, GitHub, the mala-lab/Awesome-Anomaly-Detection-Foundation-Models list).

## Short answer

**Nobody has done exactly this, but there is one close paper.** The novelty statement needs to be narrowed slightly.

- **TiRex (first version)** has already been used for anomaly detection: IBM, April 2026 (see below). But without SMD, without server data and without comparison to LSTM/GRU.
- **TiRex-2** and **Toto / Toto 2.0** have not been evaluated for anomaly detection — nothing found.
- **On SMD**, foundation models have been tested, but older ones (Chronos, TimesFM, MOMENT, TTM), and not as "pretrained model vs. model trained per server", and without cold start.

## What we found

| Paper | What they did | How it differs from us |
|---|---|---|
| **Adaptive Conformal Anomaly Detection with Time Series Foundation Models for Signal Monitoring** — Martinez Gil et al., IBM Research, 22.04.2026 · [arXiv](https://arxiv.org/abs/2604.20122) | Use pretrained forecasters (TTM, Chronos-Bolt, **TiRex**) and turn forecast errors into alarms with a label-free (conformal) threshold. Best results with TiRex. Data: YAHOO, NEK, NAB, MSL, IOPS, STOCK, WSD; multivariate TAO, GECCO, Genesis, LTDB. | **Closest to us.** But: no SMD or server data, no TiRex-2 or Toto, no comparison with per-server LSTM/GRU, no cold start. Their VUS-PR (~0.44) is slightly below MOMENT (0.461). Useful for our E4 (label-free threshold). |
| **TAB: Unified Benchmarking of Time Series Anomaly Detection Methods** — Qiu et al., PVLDB 2025 · [PDF](https://www.vldb.org/pvldb/vol18/p2775-hu.pdf) | Large benchmark including SMD and foundation models (Timer, TTM, TimesFM, UniTS, MOMENT, DADA, Chronos). Conclusion: foundation models currently perform relatively poorly. | No TiRex or Toto; no SMD-specific conclusions. |
| **Forecast2Anomaly (F2A)** — Hassan et al., HPE, 05.11.2025 · [arXiv](https://arxiv.org/pdf/2511.03149v1) | Fine-tune foundation models (TTM, TSPulse, MOMENT) for anomaly prediction on 16 TSB-AD-M datasets, including SMD. | Different models, and fine-tuning rather than zero-shot vs. LSTM/GRU. |
| **STAR** (10.2025, [arXiv](https://arxiv.org/abs/2510.16014)) and **RATFM** (06.2025, [arXiv](https://arxiv.org/abs/2506.02081)) | Add-ons to foundation models for anomaly detection. | Not TiRex/Toto, not SMD. |
| [smd-anomaly-benchmark](https://github.com/zanayeva-cyber/smd-anomaly-benchmark) — Pashaev, Zanaeva, 2026 (submitted to a journal) | Comparison on SMD: Isolation Forest, LSTM, LSTM autoencoder, CUSUM; counts false alarms per day. | No foundation models. Similar idea of counting false alarms — worth citing. |

**Checked, nothing found:** "TiRex-2 anomaly detection", "Toto anomaly detection" (only Datadog's claims, no evaluation on labelled anomalies), NX-AI's TiRex page (no mention of anomalies), the Awesome-Anomaly-Detection-Foundation-Models list (no TiRex, Toto or SMD).

## Novelty statement

> To our knowledge, **TiRex-2** and **Toto 2.0** have not yet been evaluated for anomaly detection, and on server metrics (SMD) no modern pretrained model has been compared with LSTM/GRU trained separately for each server, taking cold start and false alarms into account. The closest work (IBM, 2026) used the first version of TiRex on other datasets.

Polish version for the consultation:

> Według naszej wiedzy modele **TiRex-2** i **Toto 2.0** nie były dotąd oceniane w wykrywaniu anomalii, a na metrykach serwerowych (SMD) nikt nie porównał nowoczesnych modeli pretrenowanych z LSTM/GRU trenowanymi osobno dla każdego serwera, z uwzględnieniem zimnego startu i fałszywych alarmów. Najbliższa praca (IBM, 2026) użyła pierwszej wersji TiRex na innych zbiorach danych.

## Limitations of the search

- Google Scholar was not checked directly — worth doing (queries: `"TiRex" anomaly detection`, `"Toto" Datadog anomaly detection`).
- Some papers were read through summary pages rather than the full PDF.
- The field moves fast: repeat the search before submission (December).
