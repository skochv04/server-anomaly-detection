# Novelty search: TiRex / Toto + anomaly detection

Item 1 for consultation 1 (23.10.2026). Searched on 21.10.2026: arXiv, Google Scholar (by hand), OpenAlex, web search, GitHub.

## Short answer

We did not identify a published study with our exact experimental setup. Close works exist, so the novelty claim is narrowed:

- **TiRex-2**: no published anomaly detection evaluation identified in our search.
- **First TiRex**: one anomaly detection study found (IBM), on other data.
- **Toto / Toto 2.0**: used for anomalies in drilling, spacecraft and one storage cluster; we found no comparison with per-server LSTM/GRU and no cold-start study.

## Closest papers

| Paper | What they did | Difference from us |
|---|---|---|
| Martinez Gil et al. (IBM), ICLR 2026 · [arXiv](https://arxiv.org/abs/2604.20122) | Used pretrained forecasting models (first TiRex, Chronos-Bolt, TTM) without training and detected anomalies from their forecast errors. Proposed W1-ACAS, an adaptive conformal calibration method that converts forecast errors into anomaly decisions and aims to control the false-alarm rate under changing data. Compared it with classical methods and trained deep models (CNN, USAD, OmniAnomaly) on TSB-AD datasets and reported the best results on threshold-based metrics. | Their main contribution is the threshold method, whereas ours is the comparison of zero-shot models with LSTM/GRU trained per server, including cold start. They do not use TiRex-2, Toto or SMD. Their best F1 scores use point-adjust and a threshold chosen on test labels, which we avoid. |
| Yum, 2026, technical report · [PDF](https://seoyoonyum.github.io/assets/pdf/papers/tsfm_ad_technical_report.pdf) | Evaluated whether a frozen Toto 2.0 (313M) model could detect infrastructure anomalies without task-specific training, using a production Ceph cluster and a frame-ingestion pipeline. Toto forecast normal latency well but failed to reliably predict future OSD failures. It detected most ongoing disturbances (39/39 Ceph and 32/34 DigitalPath proxy events), although alert precision was low (4–14%). On TSB-AD-M, a simple baseline outperformed Toto's forecasting residuals (VUS-PR 0.29 vs. 0.14). The author concluded that foundation models are useful as initial anomaly signals but cannot replace operational monitoring rules. | This single-author technical report uses operational data with proxy labels derived from monitored signals, limiting independent validation. Unlike our study, it does not systematically compare zero-shot foundation models against server-specific LSTM/GRU models or investigate how detection performance changes with the amount of available training data (cold start). Its TSB-AD-M experiment was offline and involved look-ahead, so it does not establish online performance. |
| Sengupta et al., ICML 2026 workshop · [page](https://icml.cc/virtual/2026/71509) | Fine-tuned Chronos-2 and the first Toto on labeled drilling anomalies and compared them with small CNN models. Chronos-2 was best (F1 0.52 / 0.69), Toto lost to a plain CNN, and a 5M CNN-FNO nearly matched Chronos-2 on torque at ~10× lower inference time. | Supervised training on labeled anomalies, not zero-shot; not server data, no TiRex, no LSTM/GRU. Their data-size test asks how much labeling a foundation model needs, our cold start asks how much normal history LSTM/GRU need to catch up with a zero-shot model. |
| Olive et al., CVPR 2026 workshop (AI4Space) · [list](https://openaccess.thecvf.com/CVPR2026_workshops/AI4Space) | Applied MOIRAI, the first Toto, Chronos and TimesFM to Mars orbiter telemetry with 27 injected synthetic anomalies, zero-shot and with fine-tuning of MOIRAI and Chronos. Zero-shot Toto was best (F1 0.752), but a small fine-tuned MOIRAI beat it (0.859) at much lower inference time (5 s vs 123 s per 1000 points). With short context the models copied recent values and missed anomalies, so long context was essential. | Synthetic anomalies, a small test set, and a lenient F1 (any overlap counts as a hit). Motivated by cold start, but does not vary the amount of training history to find when local training pays off. No TiRex-2, Toto 2.0, trained LSTM/GRU or simple baselines; we take from it the need for long context and an early check of Toto's speed. |
| Zhu et al., ICLR 2026 · [page](https://mlanthology.org/iclr/2026/zhu2026iclr-foundation/) | Ran five families of foundation models (MOMENT, Chronos-Bolt, TimesFM, Time-MoE, TSPulse) zero-shot on 350 univariate TSB-AD-U series with different sizes and context lengths. Standard forecasting- and reconstruction-error scores did not significantly outperform two one-line baselines: one-step forecasts adapt to ongoing anomalies, and reconstruction scores largely reflect local variance. Longer forecasting horizons improve detection of sustained anomalies but reduce sensitivity to short ones. | Primarily univariate evaluation, with only qualitative multivariate checks of Toto 1.0 and Chronos-2. No TiRex-2 or Toto 2.0, and no comparison with locally trained LSTM/GRU under cold start. We include their baselines (moving-window variance and Last-3) and choose the forecast horizon with their finding in mind. |
| Qiu et al. (TAB), PVLDB 2025 · [PDF](https://www.vldb.org/pvldb/vol18/p2775-hu.pdf) | Evaluated 40 methods on 29 multivariate datasets (including SMD) and 46 methods on 1,635 univariate series, covering classical ML, deep learning (incl. LSTM, TranAD) and older pretrained models (TimesFM, Chronos, MOMENT) under zero-shot, few-shot and full-shot settings, without point-adjust. In their experiments, zero-shot pretrained models were clearly weaker than fine-tuned ones, no method dominated across anomaly types, and simple methods (KNN, KMeans) were among the best. Accuracy must be weighed against training time, inference time and memory. | TAB provides a broad benchmark rather than investigating the specific cold-start crossover between frozen foundation models and lightweight models trained separately for each server. Our study varies the amount of available normal training history (10–100%) for LSTM/GRU and compares them with TiRex-2, Toto 2.0, and simple baselines on SMD. We also use thresholds calibrated without test labels, whereas TAB reports the best results across several evaluated thresholds. |
| Varverakis et al., Future Internet 2026 · [MDPI](https://www.mdpi.com/1999-5903/18/10/550) | Evaluated Chronos-2, TimesFM-2.5 and the first TiRex zero-shot under random missingness, long outages and injected spikes on univariate industrial sensor data (SKAB), measuring forecast RMSE and interval coverage. Random gaps and sparse spikes changed forecasts by less than 3%, while long outages caused much larger errors, especially for TimesFM-2.5. | Forecasting robustness only, not anomaly detection; no TiRex-2, Toto, SMD, trained LSTM/GRU or cold start. Shows that a past spike barely moves the forecast, which limits false alarms after an anomaly but says nothing about whether the anomaly itself is detected. |

## Novelty statement

> To our knowledge, nobody has measured how much normal history LSTM/GRU trained per server need to catch up with zero-shot foundation models on server metrics (SMD). We study this cold-start crossover with **TiRex-2**, which has not yet been evaluated for anomaly detection, and **Toto 2.0**, together with simple baselines, label-free thresholds and false alarms. Earlier works compared older pretrained models with trained ones without varying the training history (TAB, 2025; IBM, 2026), checked the first Toto only qualitatively (Zhu, 2026), or used Toto on other data: drilling, spacecraft and one storage cluster (Sengupta, Olive, Yum, 2026).


## What this means for the plan

**Goal.** Find out under which conditions zero-shot foundation models give a practical advantage over LSTM/GRU trained per server and over simple statistical methods, taking into account the amount of available history, detection quality and computational cost.

Items marked *general practice* did not come from these papers but are needed for a fair comparison.

### Core experiments

1. **Models:** TiRex-2, Toto 2.0 (report the exact checkpoint size), LSTM, GRU. Baselines: Isolation Forest, Last-3 and moving-window variance. No extra models until the core is done. (Zhu: foundation models are not better than the one-liners; TAB: KNN/KMeans among the best; Yum, Olive: results depend on model size)
2. **Cold start:** LSTM/GRU trained on the first consecutive 10 / 25 / 50 / 100% of the train split (not random points, so it mimics a server accumulating history), compared with the zero-shot models. Report the absolute number of points and days for each fraction. Define the crossover in advance, e.g. the smallest fraction at which the mean VUS-PR of LSTM/GRU is not lower than that of the zero-shot model, with the spread across seeds. This is our novelty. (Olive names cold start as motivation but does not measure it; TAB's few-shot fine-tunes the pretrained model instead)
3. **Long context** for TiRex-2 and Toto, starting with 512–1024 points where supported: with short context the models copy recent values and miss anomalies. Do not assume that longer context always helps. (Olive, Zhu)
4. **Same forecast horizon for all models.** A one-step forecast misses long anomalies, a long horizon misses short ones. (Zhu)
5. **Decide in advance how the 38 metrics of a server become one anomaly score**, e.g. the mean forecast error across metrics. (Zhu, Olive use the mean squared error across channels)

### Fair evaluation

6. **Threshold from training or validation data only, never from test labels, with the same protocol for all models, including zero-shot ones.** "Zero-shot" means frozen weights, not zero calibration. Unlabeled anomalies in the SMD train split may contaminate the threshold; mention this as a limitation. (Yum; IBM and TAB chose thresholds on test labels, which we avoid)
7. **No point-adjust** and no "any overlap counts as a hit". (IBM, Olive use these)
8. **Normalization statistics from the train split only.** (*general practice*)
9. **Online setting, no look-ahead:** a model never sees values after the point it scores. (Yum: his TSB-AD-M check and the TimeRCD run used future values, so those numbers are not reliable)
10. **Count alarms as events** and report the share of alarms that match a real anomaly, not only alarms per day or per 1000 points. Fix in advance the rule for merging adjacent alarm points and the criterion for matching an alarm to an anomaly. (Yum: 1.5 alarms/day, but only 4–14% correct)
11. **Several seeds for LSTM/GRU**, report mean and spread. (*general practice*)

### Cost

12. **Measure training time, inference time and memory.** Time Toto in the pilot: it can be over 20× slower than other models. (Olive: 123 s vs 5 s per 1000 points; TAB: accuracy must be weighed against time and memory)

### Analysis and report

13. **Look at results per server, not only the average**, and compare forecast errors on normal and anomalous windows to explain *why* a model works or fails, including whether Toto adapts to long anomalies. (Zhu: aggregate metrics hide the real behaviour; Yum: Toto adapts to a sustained new level)
14. **Do not claim to be first** to apply foundation models to anomaly detection or to compare them with trained models. Our novelty is narrower: when per-server LSTM/GRU become competitive with 2026 zero-shot models on server metrics. (IBM, TAB, Sengupta already compare pretrained and trained models)
15. **Limitations:** one main dataset, questionable labels in part of SMD, possible presence of SMD in the models' pretraining data. Check the TiRex-2 and Toto 2.0 documentation for their pretraining datasets; if SMD was used, results on it are not fully zero-shot. (Zhu flag two SMD-derived univariate series in TSB-AD-U, IDs 68 and 74, as mislabeled, and checked pretraining contamination for MOMENT)
16. **A negative result is still a result.** (Zhu, Yum, TAB: foundation models often lose to simple methods)

### Only if time allows

- Several forecast horizons, short and long, taking the maximum error. (Zhu)
- Mean vs. max aggregation of errors across the 38 metrics: a mean can hide an anomaly that appears in only one metric. Cheap, since the per-metric errors are the same.
- A second dataset: OS-Metrics, PSM or Exathlon.