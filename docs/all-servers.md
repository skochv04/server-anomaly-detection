# Results on all 22 servers

## What changed since the pilot

The pilot used one server and only simple methods. Now every method runs on all 22 SMD servers, and two new models are added: an LSTM trained separately for each server and the pretrained TiRex-2 used without any training.

## Data

The data is the same as in the pilot: 22 servers from the TSB-AD version of SMD, 38 metrics per minute. The training parts are short, between 500 and 7,180 minutes, while the test parts are between about 17,800 and 27,700 minutes long. All metrics are brought to the same scale using the mean and standard deviation of the training part only.

## Methods

Last-3, moving-window variance and Isolation Forest work as in the pilot. The variance window is no longer fixed at 30 minutes. TSB-AD chooses it for each server from the typical period of the first metric, and it was 30 on the pilot server. Isolation Forest is again run with five random seeds.

LSTM is the TSB-AD implementation. It looks at the last 100 minutes and predicts the values of all 38 metrics in the next minute. It is trained on the training part of the same server only, and part of that data is held out to stop training once the model no longer improves. The score of a minute is the prediction error: the squared difference between the predicted and the real value, averaged over the 38 metrics. We trained it with three random seeds.

TiRex-2 is a pretrained forecasting model, and its weights are not changed. It receives up to 512 previous minutes and forecasts the next 10 minutes, then moves 10 minutes forward and forecasts again. At the start of a series it gets as much history as exists. The model gives a range of possible values, and we take the middle one (the median). The score is computed in the same way as for LSTM: the squared error of the forecast, averaged over the 38 metrics. We keep the error of every metric separately, so other ways of combining them can be tested without running the model again.

## Evaluation

As in the pilot, the main measure is VUS-PR on the test part, and F1 is taken at the best threshold on the test part, so it is optimistic. For each method we report the mean and the median over the 22 servers, on how many servers it was the best, and its average place among the five methods (1 is best, 5 is worst). For methods with several seeds, we first average the seeds on each server.

## Results

| Method | Mean VUS-PR | Median VUS-PR | Best on | Average place | Mean F1 | Time per server |
|---|---|---|---|---|---|---|
| LSTM (3 seeds) | 0.448 | 0.402 | 8 | 2.55 | 0.505 | 8 s with training, laptop GPU |
| Moving-window variance | 0.418 | 0.398 | 8 | 2.36 | 0.482 | below 0.01 s |
| TiRex-2 | 0.360 | 0.280 | 0 | 3.45 | 0.386 | about 6 min, one V100 GPU |
| Last-3 | 0.343 | 0.260 | 3 | 3.27 | 0.393 | below 0.01 s |
| Isolation Forest (5 seeds) | 0.298 | 0.260 | 3 | 3.36 | 0.453 | 3 s, CPU |

LSTM has the highest mean, but the moving-window variance is close behind, wins on as many servers and has the better average place. It needs no training and is computed almost instantly.

TiRex-2 did not reach either of them. It scored higher than LSTM on 7 of the 22 servers, higher than the variance also on 7, and it was not the best method on any server. Its mean is close to the simple methods, and it needs a GPU and several minutes per server. On the laptop GPU it took about an hour per server, so the full run was done on the PLGrid Ares cluster, where the 22 servers ran in parallel. This agrees with Zhu et al. (ICLR 2026) and Yum (2026), who also found that pretrained models did not beat simple baselines.

The servers differ a lot. On one server all methods score about 0.95, on another all of them stay below 0.1. An average over 22 servers hides this, so the per-server results are given below.

LSTM gives almost the same result with every seed (the scores differ by about 0.005 on a server). Isolation Forest changes more, by about 0.02.

## Mean or maximum over the metrics

A mean over 38 metrics could hide an anomaly that shows up in only one of them. We therefore also tried the largest error among the 38 metrics instead of the mean. It made every method slightly worse:

| Method | Mean over metrics | Maximum over metrics | Servers where the maximum is better |
|---|---|---|---|
| TiRex-2 | 0.360 | 0.344 | 3 of 22 |
| Moving-window variance | 0.418 | 0.404 | 4 of 22 |
| Last-3 | 0.343 | 0.333 | 6 of 22 |

In SMD an anomaly usually affects several metrics at once, so the mean picks it up better, while the maximum also reacts to a jump in a single noisy metric. We keep the mean. The weaker result of TiRex-2 does not come from the way the metrics are combined.

## Results per server (VUS-PR)

| Server | LSTM | Variance | TiRex-2 | Last-3 | Isolation Forest |
|---|---|---|---|---|---|
| 057 | 0.347 | 0.375 | 0.189 | 0.152 | 0.313 |
| 058 | 0.528 | 0.542 | 0.529 | 0.583 | 0.647 |
| 059 | 0.455 | 0.289 | 0.314 | 0.383 | 0.329 |
| 060 | 0.426 | 0.657 | 0.293 | 0.216 | 0.079 |
| 061 | 0.216 | 0.276 | 0.164 | 0.150 | 0.365 |
| 062 | 0.883 | 0.695 | 0.867 | 0.807 | 0.259 |
| 063 | 0.399 | 0.426 | 0.223 | 0.234 | 0.282 |
| 064 | 0.272 | 0.384 | 0.390 | 0.405 | 0.191 |
| 065 | 0.733 | 0.224 | 0.231 | 0.211 | 0.248 |
| 066 | 0.669 | 0.236 | 0.138 | 0.110 | 0.440 |
| 067 | 0.033 | 0.097 | 0.060 | 0.069 | 0.061 |
| 068 | 0.406 | 0.558 | 0.488 | 0.455 | 0.260 |
| 069 | 0.289 | 0.412 | 0.242 | 0.272 | 0.259 |
| 070 | 0.348 | 0.352 | 0.326 | 0.299 | 0.123 |
| 071 | 0.382 | 0.681 | 0.654 | 0.461 | 0.245 |
| 072 | 0.707 | 0.629 | 0.564 | 0.618 | 0.427 |
| 073 | 0.292 | 0.208 | 0.267 | 0.196 | 0.270 |
| 074 | 0.585 | 0.493 | 0.236 | 0.093 | 0.265 |
| 075 | 0.659 | 0.164 | 0.233 | 0.248 | 0.106 |
| 076 | 0.952 | 0.953 | 0.936 | 0.938 | 0.967 |
| 077 | 0.185 | 0.419 | 0.417 | 0.434 | 0.209 |
| 078 | 0.095 | 0.130 | 0.164 | 0.212 | 0.200 |

## Limitations

F1 still uses a threshold chosen on the test part. A threshold taken from the training part, and the number of false alarms it produces, are the next step.

LSTM predicts one minute ahead, TiRex-2 ten minutes ahead. The comparison is therefore not yet made at the same forecast horizon.

TiRex-2 was run with one setting only: 512 minutes of history and a 10-minute forecast.

Isolation Forest is still fitted on the whole series, including the test part.

We have not yet checked whether SMD was part of the data TiRex-2 was trained on. If it was, its results here are not fully zero-shot.

## What this means for the plan

LSTM trained on the full history is better than TiRex-2. The cold-start experiment will show whether this still holds when LSTM gets only a little history. Because the moving-window variance also needs no training and is better than TiRex-2, LSTM with little history should be compared with both of them.

The training parts are short, so the amounts of history for the cold start are better given in minutes than in percent. With 10% of the shortest training part, LSTM would get 50 minutes, less than the 100 it looks at.

Next come Toto 2.0 and GRU on all servers, then the threshold from the training part and the false alarms.
