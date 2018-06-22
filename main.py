import os
from glob import glob
import json
from PIL import Image
import cv2
import numpy as np
import re

from process_videos import process_videos


def crop_image(frame, tag):
    (top, bot, left, right) = (tag["top"], tag["bot"], tag["left"], tag["right"])
    print("Top:{} Bot:{} Left:{} Right:{}".format(top, bot, left, right))

    (height, width) = frame.shape[0:2]
    pad = 0.05

    if top < pad * height or bot > (1-pad) * height or left < pad * width or right > (1-pad) * width:
        return None

    img = frame[...,::-1]
    return Image.fromarray(img[top:bot, left:right])


def target_search(cap, output_dir, target="car"):
    frame_idx = 1
    suc, frame = cap.read()

    if not suc:
        print("Unable to read video")
        return

    target_dir = os.path.join(output_dir, target)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    data_file = os.path.join(output_dir.replace("output", "frames"), "frame.txt")
    if not os.path.isfile(data_file):
        print("File not found", data_file)
        return

    os.system("cp {} {}".format(data_file, output_dir))

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
                    img = crop_image(frame, tag)

                    if img is not None:
                        file = os.path.join(target_dir, framename.replace(".jpg", "_obj_{:03d}.jpg".format(idx+1)))
                        img.save(file)
                        print(file)
                        cnt += 1

    print("Found {} with tag {}.".format(cnt, target))
    print(output_dir)
    os.system("ls -l {} | wc -l".format(target_dir))

process_videos()

input_dirs = sorted(glob("input/*"))
# input_dirs = ["input/982"]
for input_dir in input_dirs:
    videos = sorted(glob(os.path.join(input_dir, "*.avi")))

    for video in videos:
        output_dir = os.path.splitext(video)[0].replace("input", "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

            cap = cv2.VideoCapture(video)
            target_search(cap, output_dir, target="car")
            cap.release()

# os.system("darknet detector demo cfg/coco.data cfg/yolo.cfg yolo.weights input/data/2017-08-16_18-07-18.avi -prefix output/frame")
