import os
from glob import glob
import json
from PIL import Image
import cv2
import numpy as np
import re

darknet_path = "/root/darknet_v2.0"
os.environ["PATH"] = darknet_path + ":" + os.environ["PATH"]

if len(glob("yolo.weights")) == 0:
    os.system("wget https://pjreddie.com/media/files/yolo.weights")


def process_video(video, output_dir):
    cmd = "darknet detector demo cfg/coco.data cfg/yolo.cfg yolo.weights {} -avg 1 -prefix {}".format(video, os.path.join(output_dir, "frame"))
    print(">", cmd)
    os.system(cmd)


def crop_image(frame, tag):
    (top, bot, left, right) = (tag["top"], tag["bot"], tag["left"], tag["right"])
    print("Top:{} Bot:{} Left:{} Right:{}".format(top, bot, left, right))

    (height, width) = frame.shape[0:1]
    pad = 0.2

    if top < pad * height or bot > (1-pad) * height or left < pad * width or right > (1-pad) * width:
        return None

    img = frame[...,::-1]
    return Image.fromarray(img[top:bot, left:right])


def target_search(frames, output_dir, target="car"):
    target_dir = os.path.join(output_dir, target)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    with open(os.path.join(output_dir, "frame.txt")) as f:
        frame_data = [line.strip() for line in f.readlines()]

    for data in frame_data:
        info = json.loads(data)
        framename = os.path.basename(info["filename"])
        tag_list = info["tag"]
        cnt = 0
        for tag in tag_list:
            if target in tag:
                framenum = int(re.sub("[^0-9]", "", framename))
                print("Frame:", framenum)

                if 0 <= framenum and framenum < len(frames):
                    img = crop_image(frames[framenum], tag)

                    if img is not None:
                        file = os.path.join(target_dir, framename.replace(".jpg", "_{}_{:02d}.jpg".format(target, cnt)))
                        img.save(file)
                        print(file)
                        cnt += 1


input_dirs = glob("input/*")
for input_dir in input_dirs:
    videos = glob(os.path.join(input_dir, "*.avi"))

    for video in videos:
        output_dir = os.path.splitext(video)[0].replace("input", "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        process_video(video, output_dir)

        cap = cv2.VideoCapture(video)
        frames = [None]
        suc, frame = cap.read()
        while suc:
            frames.append(frame)
            suc, frame = cap.read()
        cap.release()
        target_search(frames, output_dir)

# os.system("darknet detector demo cfg/coco.data cfg/yolo.cfg yolo.weights input/data/2017-08-16_18-07-18.avi -prefix output/frame")
