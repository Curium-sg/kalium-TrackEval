from collections import defaultdict
import os
import argparse
import sys


def convert_labels_to_motc_format(labels_path, is_gt=False, skip_frames=0):
    label_list = sorted([f for f in os.listdir(labels_path) if f.endswith('.txt')])
    frame_num = 1
    labels_new = []
    id_numbers = defaultdict()
    for idx, label in enumerate(label_list):
        with open(os.path.join(labels_path, label), 'r') as f:
            lines = f.readlines()
        used_ids = set()
        if idx < skip_frames:
            continue
        for line in lines:
            tokens = line.strip().split()
            id = tokens[-2]
            if id not in id_numbers:
                id_numbers[id] = len(id_numbers) + 1
            id = id_numbers[id]
            if id in used_ids: # if id already used in this frame, skip
                print(f"ID {id} already used, skipping.")
                continue
            used_ids.add(id)
            conf = 1
            x = tokens[0]
            y = tokens[1]
            z = tokens[2]
            dx = tokens[3]
            dy = tokens[4]
            dz = tokens[5]

            # top left corner of the bounding box
            bb_left = float(x) - float(dx) / 2
            bb_top = float(y) + float(dy) / 2
            bb_width = float(dx)
            bb_height = float(dy)

            if is_gt:
                labels_new.append(",".join([
                    str(frame_num),
                    str(id),
                    str(bb_left),
                    str(bb_top),
                    str(bb_width),
                    str(bb_height),
                    str(-1),
                    str(-1),
                    str(-1)
                ]))
            else:
                labels_new.append(",".join([
                    str(frame_num),
                    str(id),
                    str(bb_left),
                    str(bb_top),
                    str(bb_width),
                    str(bb_height),
                    str(conf),
                    str(-1),
                    str(-1),
                    str(-1)
                ]))
        frame_num += 1
            
    return labels_new, len(label_list) - skip_frames

def write_labels_to_file(labels_new, output_path):
    with open(output_path, 'w') as f:
        for label in labels_new:
            f.write(label + '\n')
    f.close()

def write_seq_ini_file(name, label_length, output_path):
    output_string = [
        "[Sequence]",
        f"name={name}",
        "imDir=img1",
        "frameRate=30",
        f"seqLength={label_length}",
        "imWidth=1920",
        "imHeight=1080",
        "imExt=.jpg",
    ]
    output_string = "\n".join(output_string)
    with open(os.path.join(output_path, "seqinfo.ini"), 'w') as f:
        f.write(output_string)
    f.close()

def create_gt_folder(dataset_name, subset_name, gt_labels_path, skip_frames, output_dir):
    labels_gt, label_length = convert_labels_to_motc_format(gt_labels_path, is_gt=True, skip_frames=skip_frames)
    gt_folder_path = os.path.join(output_dir,
        "gt", "mot_challenge", f"{dataset_name}-test")
    os.makedirs(gt_folder_path, exist_ok=True)
    seq_info_dir = os.path.join(gt_folder_path, subset_name)
    os.makedirs(seq_info_dir, exist_ok=True)
    write_seq_ini_file(subset_name, label_length, seq_info_dir)
    labels_gt_output_dir = os.path.join(seq_info_dir, "gt")
    os.makedirs(labels_gt_output_dir, exist_ok=True)
    write_labels_to_file(labels_gt, os.path.join(labels_gt_output_dir, "gt.txt"))
    print(f"Wrote to GT label directory: {gt_folder_path}")

def create_eval_folder(dataset_name, exp_name, subset_name, eval_labels_path, skip_frames, output_dir):
    labels_eval, _ = convert_labels_to_motc_format(eval_labels_path, is_gt=False, skip_frames=skip_frames)
    eval_folder_path = os.path.join(output_dir,
        "trackers", "mot_challenge", f"{dataset_name}-test")
    os.makedirs(eval_folder_path, exist_ok=True)
    tracker_name = exp_name
    tracker_dir = os.path.join(eval_folder_path, tracker_name)
    os.makedirs(tracker_dir, exist_ok=True)
    data_dir = os.path.join(tracker_dir, "data")
    os.makedirs(data_dir, exist_ok=True)
    write_labels_to_file(labels_eval, os.path.join(data_dir, f"{subset_name}.txt"))
    print(f"Wrote to eval label directory: {eval_folder_path}")

def create_seqmap_file(dataset_name, subset_names, output_dir):
    output_string = ["dataset"]
    output_string.extend(subset_names)
    output_string = "\n".join(output_string)
    seqmap_path = os.path.join(output_dir,
        "gt", "mot_challenge", "seqmaps")
    os.makedirs(seqmap_path, exist_ok=True)
    seqmap_filename = os.path.join(seqmap_path, f"{dataset_name}-test.txt")
    with open(os.path.join(os.getcwd(), seqmap_filename), 'w') as f:
        f.write(output_string)
    f.close()
    print(f"Wrote seqmap file: {seqmap_filename}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert labels to MOTC format.")
    parser.add_argument("--dataset_name", type=str, required=True, help="Name of the dataset.")
    parser.add_argument("--exp_name", type=str, default="kalium", help="Name of the experiment.")
    parser.add_argument("--gt_labels", type=str, nargs='+', required=True, help="Path to the gt labels directory.")
    parser.add_argument("--eval_labels", type=str,nargs='+', required=True, help="Path to the evaluation labels directory.")
    parser.add_argument("--skip_frames", type=int, default=0, help="Number of frames to skip.")
    default_output_dir = os.path.join(os.getcwd(), "..", "data")
    parser.add_argument("--output_dir", type=str, default=default_output_dir, help="Output directory for the converted labels.")
    args = parser.parse_args()

    dataset_name = args.dataset_name
    exp_name = args.exp_name
    gt_labels_paths = args.gt_labels
    eval_labels_paths = args.eval_labels
    skip_frames = args.skip_frames
    output_dir = args.output_dir

    assert len(gt_labels_paths) == len(eval_labels_paths), "Number of gt and eval labels must be the same."
    subset_names = [labels_path.split("/")[-2] for labels_path in gt_labels_paths]
    for gt_labels_path, eval_labels_path, subset_name in zip(gt_labels_paths, eval_labels_paths, subset_names):
        assert os.path.exists(gt_labels_path), f"GT labels path {gt_labels_path} does not exist."
        assert os.path.exists(eval_labels_path), f"Eval labels path {eval_labels_path} does not exist."
        # Create GT folder
        create_gt_folder(dataset_name, subset_name, gt_labels_path, skip_frames, output_dir)
        # Create Eval folder
        create_eval_folder(dataset_name, exp_name, subset_name, eval_labels_path, skip_frames, output_dir)
    create_seqmap_file(dataset_name, subset_names, output_dir)