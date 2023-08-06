#!/bin/bash
#PBS -N crawlingJob
#PBS -l nodes=1:ppn=1
#PBS -l walltime=00:30:00

curl -X POST -u admin:admin pbs_sim_node_placeholder:8000/api/runners/start-docker/ -H 'Content-Type: application/json' -d '{"id": runner_placeholder, "description": "","name": "test","crawler": crawler_placeholder}'
