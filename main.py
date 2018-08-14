# -*- coding: utf-8 -*-
import cv2
import re
import os
import sys
import json
from subprocess import Popen, PIPE
from glob import glob

from lib.progress_bar import print_progress
from lib.std_redirect import stderr_redirected


def detect_video(video_path, frames_dir, data_file="cfg/coco.data", cfg_file="cfg/yolov2.cfg", weights_file="weights/yolov2.weights"):
    prefix = os.path.join(frames_dir, os.path.splitext(os.path.basename(video_path))[0], "frame")
    os.makedirs(os.path.dirname(prefix), exist_ok=True)

    with stderr_redirected(to=sys.stdout.fileno()):
        process = Popen(["darknet", "detector", "demo", data_file, cfg_file, weights_file, video_path,
                         "-avg", "1", "-prefix", prefix], stdout=PIPE)

        print("Detecting ", os.path.basename(video_path), "...")

        while process.poll() is None:
            output = process.stdout.readline().decode("utf-8")
            try:
                obj = json.loads(output)

                if obj["type"] == "UPDATESTATUS":
                    progress = obj["data"]["progress"]
                    print_progress(progress, 100, prefix="Progress:", suffix="Complete", bar_length=50)
            except ValueError as e:
                continue

        print()


def crop_image(frame, tag, pad=0):
    (top, bot, left, right) = (tag["top"], tag["bot"], tag["left"], tag["right"])
    # print("Top:{} Bot:{} Left:{} Right:{}".format(top, bot, left, right))

    (height, width) = frame.shape[0:2]

    if top < pad * height or bot > (1-pad) * height or left < pad * width or right > (1-pad) * width:
        return None

    return frame[top:bot, left:right]


def target_search(file, frames_txt, output_dir, target):
    if not os.path.isfile(frames_txt):
        print("File not found", frames_txt, file=sys.stderr)
        return

    cap = cv2.VideoCapture(file)

    frame_idx = 1
    (suc, frame) = cap.read()

    if not suc:
        print("Unable to read video", file=sys.stderr)
        cap.release()
        return

    target_dir = os.path.join(output_dir, target)
    os.makedirs(target_dir, exist_ok=True)

    with open(frames_txt) as f:
        frame_data = [line.strip() for line in f.readlines()]

    cnt = 0

    for data in frame_data:
        info = json.loads(data)
        framename = os.path.basename(info["filename"])
        tag_list = info["tag"]

        for idx, tag in enumerate(tag_list):
            if target not in tag:
                continue

            framenum = int(re.sub("[^0-9]", "", framename))
            while frame_idx < framenum:
                cap.grab()
                frame_idx += 1
            suc, frame = cap.retrieve()

            if suc:
                img = crop_image(frame, tag)

                if img is not None:
                    file = os.path.join(target_dir, framename.replace(".jpg", "_obj_{:03d}.jpg".format(idx + 1)))
                    cv2.imwrite(file, img)
                    cnt += 1

    print("%d items found with tag '%s'." % (cnt, target))

    cap.release()


input_dir = "input"
frames_dir = "frames"
output_dir = "output"

os.makedirs(frames_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)

files = glob(os.path.join(input_dir, "*"))

for file in files:
    frames_txt = os.path.join(os.path.splitext(file.replace(input_dir, frames_dir))[0], "frame.txt")
    if not os.path.isfile(frames_txt):
        detect_video(os.path.join(os.getcwd(), file), frames_dir)

    target_search(file, frames_txt, os.path.join(output_dir, os.path.splitext(os.path.basename(file))[0]), target="car")



