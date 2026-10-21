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

### Two rules for a fair comparison

1. The alarm threshold is chosen on the train part only, never on test labels.
2. All models forecast the same number of steps ahead.

## Plan

We go step by step and do each stage together. Tasks within a stage are split as convenient, and both of us finish the stage before moving on to the next one.

| When | To do | To show |
|---|---|---|
| **23.10** | Novelty search: TiRex / Toto + anomaly detection (results). Research questions and plan | Plan and research questions |
| **06.11** | Install TSB-AD, run Isolation Forest and TiRex-2 on **one** server | First results on one server |
| **27.11** | Add LSTM, GRU, Toto. Run everything on **3–5** servers | First comparison table |
| **11.12** | Run everything on **all** servers. Cold start: train LSTM/GRU on 10 / 25 / 50 / 100% of the data. Compare Toto vs. TiRex-2 and count false alarms | Full results and plots |
| **08.01** | Finish the report (draft by ~20.12) | Submission |

**Optional**, only if everything is ready by 11.12: a second dataset (OS-Metrics), Chronos-2 as a third pretrained model, fine-tuning, a publication.

## Status

Consultation 1 (23.10.2026): plan and novelty check.

- [x] Novelty search: has anyone evaluated TiRex / Toto for anomaly detection? → [`docs/novelty-search.md`](docs/novelty-search.md)
- [x] Project plan (above)

## Repository structure

```
server-anomaly-detection/
├── README.md
└── docs/
    └── novelty-search.md   # has anyone done this already?
```

Code, data instructions and the literature review will be added for consultation 2 (06.11.2026).
