#!/bin/bash

# conversion script params
DATASET_NAME="lab-leap"
GT_LABELS="/home/curium/Desktop/track-reconciliation/lab-leap/bbox"
EVAL_LABELS="/home/curium/Desktop/kalium_ros/test_leap/bbox"
SKIP_FRAMES=5 # default 0
OUTPUT_DIR="../data" # default "../data"

python convert_to_motc_format.py \
    --dataset_name $DATASET_NAME \
    --gt_labels $GT_LABELS \
    --eval_labels $EVAL_LABELS \
    --skip_frames $SKIP_FRAMES \
    --output_dir $OUTPUT_DIR

python run_mot_challenge.py \
    --BENCHMARK $DATASET_NAME \
    --SPLIT_TO_EVAL test \
    --TRACKERS_TO_EVAL MPNTrack \
    --METRICS HOTA CLEAR Identity VACE \
    --USE_PARALLEL True \
    --NUM_PARALLEL_CORES 4 \
    --DO_PREPROC False