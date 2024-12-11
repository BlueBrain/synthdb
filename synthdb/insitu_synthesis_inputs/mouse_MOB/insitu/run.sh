#!/bin/bash -l
#SBATCH --ntasks=80
##SBATCH --qos=longjob
#SBATCH --time=02:00:00
#SBATCH --partition=prod
#SBATCH --exclusive
#SBATCH --mem=0
#SBATCH --constraint=cpu
#SBATCH --cpus-per-task=1
#SBATCH --account=proj82

export OMP_NUM_THREADS=1

python -m luigi --module synthesis_workflow.tasks.workflows ValidateSynthesis \
    --local-scheduler \
    --log-level INFO \
