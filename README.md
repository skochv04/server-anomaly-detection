# server-anomaly-detection

**Can pretrained time-series models detect server anomalies without training?**
Zero-shot TiRex-2 & Toto 2.0 vs. per-server LSTM/GRU on SMD.

Course project, *Uczenie maszynowe*, AGH University of Krakow (2026/27).
Team: Stas Kochevenko, Diana Hunchak.

## Research questions

1. **Main.** Does a pretrained model with no training on our data (zero-shot) find anomalies in server metrics as well as LSTM/GRU trained separately for each server?
2. **Cold start.** How much history does LSTM/GRU need to catch up with a zero-shot model? We train on 10 / 25 / 50 / 100% of the train split.
3. **Domain.** Does pretraining on server metrics help? Toto 2.0 (Datadog, observability data) vs. TiRex-2 (general-purpose).
4. **Operations.** How many false alarms does each model raise when the threshold is chosen without labels, as in production?

## Approach

All forecasting models share one pipeline; only the forecaster changes.

```
server metrics → model forecast → forecast error → anomaly score → threshold → alarm
```

| Model | Mode |
|---|---|
| Isolation Forest | baseline, no temporal context |
| LSTM | trained per server |
| GRU | trained per server |
| TiRex-2 | zero-shot, xLSTM |
| Toto 2.0 (small) | zero-shot, observability-pretrained |

**Data:** SMD (Server Machine Dataset), cleaned version from [TSB-AD](https://github.com/TheDatumOrg/TSB-AD).
**Main metric:** VUS-PR; plus F1 without point-adjust and false alarms at a label-free threshold.

## Status

Consultation 1 (23.10.2026): plan and novelty check.

- [x] Novelty search: has anyone evaluated TiRex / Toto for anomaly detection? → [`docs/novelty-search.md`](docs/novelty-search.md)
- [x] Project plan → [`docs/plan.md`](docs/plan.md)

## Repository structure

```
server-anomaly-detection/
├── README.md
└── docs/
    └── novelty-search.md   # has anyone done this already?
```

Code, data instructions and the literature review will be added for consultation 2 (06.11.2026).
