# Server anomaly detection

**Can pretrained time-series models detect server anomalies without training?**
Zero-shot TiRex-2 & Toto 2.0 vs. per-server LSTM/GRU on SMD.

Course project, *Uczenie maszynowe*, AGH University of Krakow (2026/27).
Team: Stas Kochevenko, Diana Hunchak.

## Research questions

1. **Main.** Does a pretrained model with no training on our data (zero-shot) find anomalies in server metrics as well as LSTM/GRU trained separately for each server?
2. **Cold start.** How much history does LSTM/GRU need to catch up with a zero-shot model? We train on growing amounts of the train split.
3. **Domain.** Does pretraining on server metrics help? Toto 2.0 (Datadog, observability data) vs. TiRex-2 (general-purpose).
4. **Operations.** How many false alarms does each model raise when the threshold is chosen without labels, as in production?

## Approach

All forecasting models share one pipeline; only the forecaster changes.

```
server metrics → model forecast → forecast error → anomaly score → threshold → alarm
```

| Model | Mode |
|---|---|
| Last-3, window variance | one-line baselines, no training |
| Isolation Forest | baseline, no temporal context |
| LSTM | trained per server |
| GRU | trained per server |
| TiRex-2 | zero-shot, xLSTM |
| Toto 2.0 (313M) | zero-shot, observability-pretrained |

**Data:** SMD (Server Machine Dataset), cleaned version from [TSB-AD](https://github.com/TheDatumOrg/TSB-AD).

**Main metric:** VUS-PR; plus F1 without point-adjust and false alarms at a label-free threshold.

### Two rules for a fair comparison

1. The alarm threshold is chosen on the train part only, never on test labels.
2. All models forecast the same number of steps ahead.

## Plan

| When | To do | To show |
|---|---|---|
| **23.10** | Novelty search: TiRex / Toto + anomaly detection (results). Research questions and plan | Plan and research questions |
| **06.11** | Install TSB-AD, run Isolation Forest, Last-3 and window variance on **one** server | First results on one server |
| **27.11** | TiRex-2, Toto 2.0, LSTM, GRU and the simple baselines on **all 22** servers. TiRex-2 and Toto run on PLGrid Ares | First comparison table: quality and time |
| **11.12** | Cold start: retrain LSTM/GRU on only the first 250 / 500 / 1,000 / 2,000 minutes of each server and on the full history, test each on the same test part, and compare with the methods that need no training (TiRex-2, Toto, window variance). Threshold: set from the train-part scores of each model, then count on test how many anomalies are found, how many alarms are false and what share of alarms is correct (adjacent alarms = one event). Uses the saved scores, no new runs | Cold-start plot: quality vs. minutes of history, with the crossover point. Table of found anomalies and false alarms per model |
| **08.01** | Per-server analysis: plot metrics, anomalies and scores on servers where TiRex-2 won (071, 064, 077) and lost (065, 066, 074), check whether the pretrained models adapt to long anomalies and which methods catch short vs. long ones. Same horizon: rerun TiRex-2 and Toto with a 1-minute forecast on Ares, as LSTM/GRU. Cost table: training time, inference time, memory. Check from the model documentation whether SMD was in the pretraining data of TiRex-2 and Toto | Final report with all results |

## Status

Consultation 1 (23.10.2026): plan and novelty check.

- [x] Novelty search: has anyone evaluated TiRex / Toto for anomaly detection? → [`docs/novelty-search.md`](docs/novelty-search.md)
- [x] Project plan (above)

Consultation 2 (06.11.2026): pilot on one server.

- [x] TSB-AD installed, simple baselines on server id 1 → [`docs/pilot.md`](docs/pilot.md)

Consultation 3 (27.11.2026): all 22 servers.

- [x] Isolation Forest, Last-3, window variance and LSTM → [`results/local.csv`](results/local.csv)
- [x] TiRex-2 zero-shot on Ares → [`results/tirex2.csv`](results/tirex2.csv)
- [x] Description of these runs → [`docs/all-servers.md`](docs/all-servers.md)
- [x] GRU → [`results/local.csv`](results/local.csv)
- [x] Toto 2.0 zero-shot on Ares → [`results/toto.csv`](results/toto.csv)
- [x] Comparison table and figures of all methods → [`docs/all-servers.md`](docs/all-servers.md)
- [ ] Agree with the supervisor how to define the amounts of history for the cold start (train parts are only 500–7,180 points long)

## Setup

Tested on Windows 11 with Python 3.12. The virtual environment and the data are not stored in the repository, so every team member sets them up locally.

1. Create a virtual environment and install the dependencies:

   ```
   python -m venv .venv
   .venv\Scripts\python -m pip install --upgrade pip
   .venv\Scripts\python -m pip install -r requirements.txt
   .venv\Scripts\python -m pip install --no-deps TSB-AD==1.5
   ```

   TSB-AD declares `numpy<2.0`, while tirex-2 needs numpy 2, so pip refuses to install both together. `requirements.txt` therefore lists the dependencies of TSB-AD directly, and TSB-AD itself is installed with `--no-deps`. It works with numpy 2 in our tests. Its deep models still use the removed `np.Inf`, so `common.py` sets `np.Inf = np.inf` before importing TSB-AD.

2. Install PyTorch with GPU support (optional, but TiRex-2 is very slow on CPU: about 500 s per 1,000 points). With an NVIDIA GPU, check the CUDA version with `nvidia-smi` and install the matching build from [pytorch.org](https://pytorch.org/get-started/locally/), for example:

   ```
   .venv\Scripts\python -m pip install --force-reinstall --no-deps torch==2.15.0 --index-url https://download.pytorch.org/whl/cu132
   ```

3. Download the data. TSB-AD-M contains 200 multivariate series from 17 datasets; we use the 22 SMD files (`057_SMD_...` to `078_SMD_...`).

   ```
   mkdir data
   curl -L -o data/TSB-AD-M.zip https://www.thedatum.org/datasets/TSB-AD-M.zip
   tar -xf data/TSB-AD-M.zip -C data
   ```

   The file name contains the train length and the first anomaly, e.g. `057_SMD_id_1_Facility_tr_4529_1st_4629.csv` has 4,529 training points and its first anomaly at point 4,629.

4. Run the scripts from the repository root:

   ```
   .venv\Scripts\python run_local.py
   .venv\Scripts\python run_tirex.py --index 0 --max-windows 64
   ```

   `run_local.py` runs Last-3, window variance, Isolation Forest, LSTM and GRU on all 22 SMD servers. It writes one row per server, method and seed to `results/local.csv` and the full anomaly scores to `scores/`. If it stops, run it again and it continues where it left off.

   `run_tirex.py` runs TiRex-2 on all servers, or on one server with `--index`. `--max-windows` makes a short speed test without saving. For every point and metric it saves the squared error of the median forecast to `scores/tirex2/`, so the way metrics are combined can be changed later without running the model again. On Windows without a C++ compiler, tirex-2 fails in `torch.compile`, so the script sets `TORCHDYNAMO_DISABLE=1`.

## Running on Ares (PLGrid)

TiRex-2 needs about one GPU hour per server, so the full run goes to Ares. Use your own GPU grant, written as `<grant>-gpu`.

One-time setup on the login node. The repository, the environment and the data go to `$SCRATCH`, because the home quota is small:

```
cd $SCRATCH
git clone https://github.com/skochv04/server-anomaly-detection.git
cd server-anomaly-detection
module purge
module load numba/0.62.0-foss-2025b
python -m venv .venv
source .venv/bin/activate
pip install --no-cache-dir torch==2.14.1 --index-url https://download.pytorch.org/whl/cu126
pip install --no-cache-dir -r requirements.txt
pip install --no-cache-dir --no-deps TSB-AD==1.5
export HF_HOME=$SCRATCH/hf
python -c "from huggingface_hub import snapshot_download; snapshot_download('NX-AI/TiRex-2')"
mkdir -p data logs
curl -L -o data/TSB-AD-M.zip https://www.thedatum.org/datasets/TSB-AD-M.zip
unzip -q data/TSB-AD-M.zip 'TSB-AD-M/*_SMD_*' -d data
```

The `numba` module is used only because it provides a working Python. PyTorch must be the CUDA 12.6 build: newer builds no longer support the V100 GPUs on Ares.

Short test first, one server and 64 windows:

```
sbatch -A <grant>-gpu --array=0 --time=00:20:00 ares/tirex.slurm --max-windows 64
```

If `logs/tirex2_*_0.out` shows `device=cuda` and a speed line, start all 22 servers as a job array:

```
sbatch -A <grant>-gpu ares/tirex.slurm
squeue --me
```

Servers that already have a score file are skipped, so a failed job can simply be submitted again. Copy the results back to the laptop with `scp -r` from `$SCRATCH/server-anomaly-detection/scores/tirex2`. Files in `$SCRATCH` are deleted after a period without use. On the full run each server took about 6 minutes on one V100.

Then build the result table on the laptop:

```
.venv\Scripts\python collect_scores.py TiRex-2 --scores scores/tirex2 --out results/tirex2.csv
```

### Toto 2.0

Toto 2.0 (`toto-2`) needs Python 3.12+ and `pandas<3` (through `gluonts`), while `requirements.txt` pins pandas 3, so it gets its own environment, `.venv-toto`. The Python modules on Ares put their own older packages on `PYTHONPATH`, which override the ones in the environment, so the environment must be put first:

```
cd $SCRATCH/server-anomaly-detection
module purge
module load numba/0.62.0-foss-2025b
python -m venv .venv-toto
source .venv-toto/bin/activate
export PYTHONPATH=$VIRTUAL_ENV/lib/python3.13/site-packages:$PYTHONPATH
pip install --no-cache-dir torch==2.14.1 --index-url https://download.pytorch.org/whl/cu126
pip install --no-cache-dir toto-2
grep -vE "^(tirex-2|pandas|numpy)==" requirements.txt > req-toto.txt
pip install --no-cache-dir -r req-toto.txt
pip install --no-cache-dir --no-deps TSB-AD==1.5
export HF_HOME=$SCRATCH/hf
python -c "from huggingface_hub import snapshot_download; snapshot_download('Datadog/Toto-2.0-313m')"
```

`ares/toto.slurm` sets the same `PYTHONPATH`. Test and full run, as for TiRex-2:

```
sbatch -A <grant>-gpu --array=0 --time=00:20:00 ares/toto.slurm --max-windows 64
sbatch -A <grant>-gpu ares/toto.slurm
```

Each server took 84-117 s on one V100. Copy `scores/toto` back to the laptop and build the table:

```
.venv\Scripts\python collect_scores.py Toto --scores scores/toto --out results/toto.csv
```

The figures in `docs/figures/` are made from the result tables:

```
.venv\Scripts\python plots.py
```

## Repository structure

```
server-anomaly-detection/
├── README.md
├── requirements.txt
├── common.py           # data loading, scaling and evaluation shared by all scripts
├── run_local.py        # simple baselines, LSTM and GRU on all servers
├── gru_ad.py           # GRU forecaster (TSB-AD LSTM with GRU layers)
├── run_tirex.py        # TiRex-2 on all servers
├── run_toto.py         # Toto 2.0 on all servers
├── plots.py            # figures from the result tables
├── collect_scores.py   # result table from saved per-metric errors
├── pilot.py            # first pilot on one server
├── ares/tirex.slurm    # Slurm job array for Ares
├── ares/toto.slurm     # the same for Toto 2.0
├── results/            # result tables
├── scores/             # anomaly scores (not in git)
├── data/               # TSB-AD-M, downloaded locally (not in git)
└── docs/
    ├── novelty-search.md
    ├── novelty-search.pl.md
    ├── pilot.md        # pilot results
    ├── all-servers.md  # results on all 22 servers
    └── figures/        # figures made by plots.py
```
