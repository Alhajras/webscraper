#!/bin/bash
#PBS -N crawlingJob
#PBS -l nodes=1:ppn=1
#PBS -l walltime=00:30:00

curl -X POST -u admin:admin pbs-sim-node:8000/api/runners/start/ -H 'Content-Type: application/json' -d '{"id": runner_placeholder, "description": "","name": "test","crawler": crawler_placeholder}'
