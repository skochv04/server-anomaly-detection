# Pilot on one server

## Goal of the project

We want to know whether pretrained time-series models (TiRex-2, Toto 2.0) can find anomalies in server metrics without any training on our data, and how much history an LSTM or GRU trained on a single server needs before it does better than them.

Before running these models, we checked how well very simple methods do on the same data. They set the minimum level a more complex model has to beat.

## Data

We use SMD (Server Machine Dataset). It contains metrics from real servers of an internet company. Every minute, 38 values are recorded for each server (for example CPU load, memory and network traffic, but the names are hidden). Experts marked the minutes in which something was wrong with the server.

We take the cleaned version of SMD from the TSB-AD benchmark, which keeps 22 of the original 28 servers. Each server has about 21,000 to 29,000 minutes of data. The first part of each series is meant for training and contains between 500 and 7,180 minutes, the rest is used for testing.

For the pilot we used one server: 23,694 minutes, of which the first 4,529 are the training part. In the test part, 2.8% of the minutes are marked as anomalous.

## Methods

Each method gives every minute a score: the higher the score, the more suspicious the minute. None of these methods is a neural network, and none of them was trained in advance.

Last-3 compares the current values with the average of the three previous minutes. If the server suddenly behaves differently from a moment ago, the score is high. For minute $t$ and metric $j$ (out of 38):

$$s_t = \frac{1}{38} \sum_{j=1}^{38} \left( x_{t,j} - \frac{x_{t-1,j} + x_{t-2,j} + x_{t-3,j}}{3} \right)^2$$

Moving-window variance looks at the last $w = 30$ minutes and measures how much the values jump around. A calm period gives a low score, an unstable one a high score:

$$s_t = \frac{1}{38} \sum_{j=1}^{38} \mathrm{Var}\left( x_{t-w+1,j}, \dots, x_{t,j} \right)$$

Isolation Forest is a classical machine learning method. It builds random trees that split the data and gives a high score to minutes that can be separated from the rest with only a few splits, because such minutes are unusual. We use the TSB-AD implementation, which looks at 30-minute windows and normalizes them itself. Its default setting lets each tree see only one of the 1,140 window values (30 minutes × 38 metrics), which gave poor and unstable results, so we let the trees use all of them. Because the trees are random, we ran it with five different random seeds and report the mean.

For Last-3 and the moving-window variance, all 38 metrics were first brought to the same scale, using the mean and standard deviation of the training part.

## Evaluation

The scores are compared with the experts' marks using VUS-PR, the main measure in TSB-AD. It ranges from 0 to 1, where 1 means that all anomalies were found without false alarms. We also report F1, which in this pilot is taken at the best possible threshold on the test part, so it is optimistic.

## Results

| Method | VUS-PR | F1 | Time |
|---|---|---|---|
| Isolation Forest (mean of 5 seeds) | 0.313 ± 0.031 | 0.457 | 1.1 s |
| Last-3 | 0.152 | 0.223 | 0.02 s |
| Moving-window variance | 0.375 | 0.493 | 0.02 s |

Moving-window variance and Isolation Forest reach a similar level, while Last-3 is clearly weaker. The difference between the first two is small compared with how much Isolation Forest changes from seed to seed, so on one server we cannot say which of them is better. Zhu et al. (ICLR 2026) found that older pretrained models were not significantly better than such simple formulas, so TiRex-2 and Toto will need to score above roughly 0.3 to 0.375 on this server to be useful.

## Limitations of the pilot

The F1 values use a threshold chosen on the test part, which is not allowed in the final evaluation. There, the threshold will be taken from the training part only.

Isolation Forest was fitted on the whole series, including the test part. In the final evaluation it will be fitted on the training part only.

The results come from a single server and may look different on the others.

## What this means for the plan

The training parts are short. On one server it is only 500 minutes, so 10% of it is just 50 minutes. For the cold-start experiment it may be better to measure history in minutes or days instead of percent.

On one server, the first anomaly appears inside the training part, so the training data is not always clean.

The next step is to run TiRex-2 on the same server and measure how long it takes, followed by LSTM, GRU and Toto on several servers.
