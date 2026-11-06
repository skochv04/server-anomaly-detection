# Pilot results (consultation 2, 06.11.2026)

## What we are doing

We check whether pretrained time-series models (TiRex-2, Toto 2.0) find anomalies in server metrics **without any training on our data**, and how much history LSTM/GRU trained per server need to catch up with them. Full plan: [README](../README.md); literature: [novelty-search.md](novelty-search.md).

## Data

- **SMD** (Server Machine Dataset): metrics of real servers of an internet company, 38 anonymised metrics per machine, 1 point per minute, anomalies labelled by experts.
- **TSB-AD** (NeurIPS 2024): a benchmark with a cleaned version of SMD, a common evaluation (VUS-PR) and ready implementations of baseline methods. We use its multivariate part, TSB-AD-M.
- TSB-AD-M keeps **22 SMD machines**, each with 21–29k points. The train part is short: **500–7,180 points** (about 8 hours to 5 days).

## First results: SMD machine id 1

23,694 points, 38 metrics, train 4,529 points, 2.8% anomalous points in the test part. Code: [pilot.py](../pilot.py).

| Method | VUS-PR | F1 | Time |
|---|---|---|---|
| Isolation Forest | 0.056 | 0.100 | 2.4 s |
| Last-3 (deviation from the mean of the last 3 points) | 0.152 | 0.223 | 0.02 s |
| Variance in a 30-point window | **0.375** | **0.493** | 0.02 s |

The simplest method is about 7× better than Isolation Forest, in line with Zhu et al. (ICLR 2026). This sets the bar TiRex-2 and Toto have to beat.

## Caveats of the pilot

- F1 is TSB-AD's Standard-F1, taken at the best threshold on the test part. The final evaluation will use a threshold from the train part only.
- Isolation Forest is fit on the whole series, including the test part (TSB-AD's unsupervised mode). To be fixed.

## Findings that affect the plan

- **Cold start:** 10% of a 500-point train part is only 50 points. History may need to be measured in points or days, not only in percent.
- **Machine id 22:** the first anomaly (point 326) lies inside the train part (500 points), so the train part is not always clean.
- The installed TSB-AD has LSTMAD and TranAD, but not xLSTMAD.

## Next step (by 27.11)

TiRex-2 on the same machine, with inference time measured; then LSTM, GRU and Toto on 3–5 machines.
