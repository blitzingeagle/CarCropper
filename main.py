import os
from glob import glob
import json
from PIL import Image
import cv2
import numpy as np
import re
from argparse import ArgumentParser

from process_videos import process_videos


def crop_image(frame, tag, pad=0.0):
    (top, bot, left, right) = (tag["top"], tag["bot"], tag["left"], tag["right"])
    print("Top:{} Bot:{} Left:{} Right:{}".format(top, bot, left, right))

    (height, width) = frame.shape[0:2]

    if top < pad * height or bot > (1-pad) * height or left < pad * width or right > (1-pad) * width:
        return None

    img = frame[...,::-1]
    return Image.fromarray(img[top:bot, left:right])


def target_search(cap, video_output, frames_dir, output_dir, target="car", padding=0.0):
    frame_idx = 1
    suc, frame = cap.read()

    if not suc:
        print("Unable to read video")
        return

    target_dir = os.path.join(video_output, target)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    data_file = os.path.join(video_output.replace(output_dir, frames_dir), "result.txt")
    if not os.path.isfile(data_file):
        print("File not found", data_file)
        return

    os.system("cp {} {}".format(data_file, video_output))

    with open(data_file) as f:
        frame_data = [line.strip() for line in f.readlines()]

    for data in frame_data:
        info = json.loads(data)
        framename = os.path.basename(info["filename"])
        tag_list = info["tag"]
        cnt = 1
        for idx, tag in enumerate(tag_list):
            if target in tag:
                framenum = int(re.sub("[^0-9]", "", framename))
                print("Frame:", framenum)

                while frame_idx < framenum:
                    cap.grab()
                    frame_idx += 1
                suc, frame = cap.retrieve()

                if suc:
                    img = crop_image(frame, tag, pad=padding)

                    if img is not None:
                        file = os.path.join(target_dir, framename.replace(".jpg", "_obj_{:03d}.jpg".format(idx+1)))
                        img.save(file)
                        print(file)
                        cnt += 1

    print(video_output)
    os.system("ls -l {} | wc -l".format(target_dir))

parser = ArgumentParser("Cropped results of YOLO.")
parser.add_argument("-t", "--target", type=str, metavar="TARGET", help="Target label from detector.")
parser.add_argument("-i", "--input", type=str, default="./videos", metavar="INPUT", help="Input video or directory.")
parser.add_argument("-f", "--frames", type=str, default="./frames", metavar="FRAMES", help="Frames directory path.")
parser.add_argument("-o", "--output", type=str, default="./output", metavar="OUTPUT", help="Output directory path.")
parser.add_argument("-p", "--padding", type=float, default=0.0, metavar="PADDING", help="Padding to ignore detections.")

args = parser.parse_args()

if args.target is None:
    parser.print_help()
    exit(0)

input_dir = args.input
frames_dir = args.frames
output_dir = args.output
target = args.target


if os.path.isfile(args.input):
    videos = [args.input]
    input_dir = os.path.dirname(input_dir)
    single = True
else:
    videos = sorted(glob(os.path.join(input_dir, "*.avi")))
    single = False

if output_dir[-1] == "/":
    output_dir = output_dir[:-1]

process_videos(input_dir, frames_dir, videos, single)

for video in videos:
    video_output = os.path.splitext(video)[0].replace(input_dir, output_dir)
    if not os.path.exists(video_output):
        os.makedirs(video_output)

        cap = cv2.VideoCapture(video)
        target_search(cap, video_output, frames_dir, output_dir, target=target, padding=args.padding)
        cap.release()

# os.system("darknet detector demo cfg/coco.data cfg/yolo.cfg yolo.weights input/data/2017-08-16_18-07-18.avi -prefix output/frame")

