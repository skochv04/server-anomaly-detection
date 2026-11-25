#!/bin/bash
#SBATCH --job-name=toto
#SBATCH --partition=plgrid-gpu-v100
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=4
#SBATCH --mem=16G
#SBATCH --time=04:00:00
#SBATCH --array=0-21
#SBATCH --output=logs/toto_%A_%a.out

cd "$SLURM_SUBMIT_DIR"
module purge
module load numba/0.62.0-foss-2025b
source .venv-toto/bin/activate
export PYTHONPATH="$VIRTUAL_ENV/lib/python3.13/site-packages:$PYTHONPATH"
export HF_HOME="$SCRATCH/hf"

python -u run_toto.py --index "$SLURM_ARRAY_TASK_ID" --batch 128 "$@"
