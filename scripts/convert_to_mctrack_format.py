import json
import os
import numpy as np
from pyquaternion import Quaternion
from tqdm import tqdm
import argparse

def transform_yaw2quaternion(yaw):
    orientation = Quaternion(np.cos(yaw / 2), 0, 0, np.sin(yaw / 2))
    return orientation

# iterate through labels
# create a list of bboxes for each frame
# create a list of frames for each scene
# the scene data is saved as json

def get_bboxes_per_frame(label_path):
    new_boxes = []
    with open(label_path, "r") as f:
        lines = f.readlines()
    for line in lines:
        tokens = line.strip().split()
        detection_score = 0.99
        category = "pedestrian"
        global_xyz = [float(tokens[0]), float(tokens[1]), float(tokens[2])]
        lwh = [float(tokens[3]), float(tokens[4]), float(tokens[5])]
        global_yaw = float(tokens[6])
        global_orientation = transform_yaw2quaternion(global_yaw)
        global_orientation_list = [
            global_orientation.w,
            global_orientation.x,
            global_orientation.y,
            global_orientation.z,
        ]
        new_bbox = {
            "detection_score": detection_score,
            "category": category,
            "global_xyz": global_xyz,
            "global_orientation": global_orientation_list,
            "global_yaw": global_yaw,
            "lwh": lwh,
            "global_velocity": [0.0, 0.0],
            "global_acceleration": [0.0, 0.0],
            "bbox_image": {
                "camera_type": None,
                "x1y1x2y2": None,
            },
        }
        new_boxes.append(new_bbox)
    return new_boxes

def generate_mctrack_json(dets_dir, output_dir, scene_name="helsinki"):
    label_list = sorted([f for f in os.listdir(dets_dir) if f.endswith(".txt")])
    all_data = {}
    scene_data_list = []
    for frame_id, label in tqdm(enumerate(label_list)):
        label_path = os.path.join(dets_dir, label)
        timestamp = int(label.split(".")[0])
        bboxes = get_bboxes_per_frame(label_path)
        scene_data = {
            "frame_id": frame_id,
            "cur_sample_token": None,
            "timestamp": timestamp,
            "bboxes": bboxes,
            "transform_matrix": {
                "global2ego": None,
                "ego2lidar": None,
                "global2lidar": None,
                "cameras_transform_matrix": None,
            },
        }
        scene_data_list.append(scene_data)
    all_data[scene_name] = scene_data_list
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "val.json"), "w") as f:
        json.dump(all_data, f, indent=4)

def parse_args():
    parser = argparse.ArgumentParser(description="Convert labels to mctrack format")
    parser.add_argument(
        "--dets_dir",
        type=str,
        default="./data/labels/",
        help="Directory containing the labels",
    )
    parser.add_argument(
        "--output_dir",
        type=str,
        default="./data/mctrack_format.json",
        help="Output path for the mctrack format json file",
    )
    parser.add_argument(
        "--scene_name",
        type=str,
        default="helsinki",
        help="Scene name for the mctrack format json file",
    )
    return parser.parse_args()

def main():
    args = parse_args()
    dets_dir = args.dets_dir
    output_dir = args.output_dir
    scene_name = args.scene_name
    generate_mctrack_json(dets_dir, output_dir, scene_name)
    print(f"Converted labels to mctrack format and saved to {output_dir}")

if __name__ == "__main__":
    main()