#!/bin/bash

# conversion script params
DATASET_NAME="helsinki"
GT_LABELS_PATHS=(
    "/home/curium/Desktop/kalium-datasets/sequences/7ls5/labels"
    "/home/curium/Desktop/kalium-datasets/sequences/7ls21/labels"
    "/home/curium/Desktop/kalium-datasets/sequences/7ls25/labels"
)
EVAL_LABELS_PATHS=(
    "/home/curium/Desktop/kalium-datasets/sequences/7ls5/labels-offline"
    "/home/curium/Desktop/kalium-datasets/sequences/7ls21/labels-offline"
    "/home/curium/Desktop/kalium-datasets/sequences/7ls25/labels-offline"
)

# DATASET_NAME="lab-leap"
# GT_LABELS_PATHS=(
#     "/home/curium/Desktop/kalium-datasets/sequences/lab_leap_1/labels"
#     "/home/curium/Desktop/kalium-datasets/sequences/lab_leap_2/labels"
#     "/home/curium/Desktop/kalium-datasets/sequences/lab_leap_3/labels"
#     "/home/curium/Desktop/kalium-datasets/sequences/lab_leap_4/labels"
#     "/home/curium/Desktop/kalium-datasets/sequences/lab_leap_5/labels"
#     "/home/curium/Desktop/kalium-datasets/sequences/lab_leap_6/labels"
# )
# EVAL_LABELS_PATHS=(
#     "/home/curium/Desktop/kalium-datasets/sequences/lab_leap_1/labels-offline"
#     "/home/curium/Desktop/kalium-datasets/sequences/lab_leap_2/labels-offline"
#     "/home/curium/Desktop/kalium-datasets/sequences/lab_leap_3/labels-offline"
#     "/home/curium/Desktop/kalium-datasets/sequences/lab_leap_4/labels-offline"
#     "/home/curium/Desktop/kalium-datasets/sequences/lab_leap_5/labels-offline"
#     "/home/curium/Desktop/kalium-datasets/sequences/lab_leap_6/labels-offline"
# )

SKIP_FRAMES=5 # should be same as the tracking min hits value
OUTPUT_DIR="../data" # default "../data"
EXP_NAME="MPNTrack"

# Convert arrays to space-separated strings
GT_LABELS_PATHS=$(IFS=' '; echo "${GT_LABELS_PATHS[*]}")
EVAL_LABELS_PATHS=$(IFS=' '; echo "${EVAL_LABELS_PATHS[*]}")

python convert_to_motc_format.py \
    --dataset_name $DATASET_NAME \
    --gt_labels $GT_LABELS_PATHS \
    --eval_labels $EVAL_LABELS_PATHS \
    --skip_frames $SKIP_FRAMES \
    --output_dir $OUTPUT_DIR

python run_mot_challenge.py \
    --BENCHMARK $DATASET_NAME \
    --SPLIT_TO_EVAL test \
    --TRACKERS_TO_EVAL $EXP_NAME \
    --METRICS HOTA CLEAR Identity VACE \
    --USE_PARALLEL True \
    --NUM_PARALLEL_CORES 4 \
    --DO_PREPROC False