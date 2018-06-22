import os
from glob import glob
import json
from PIL import Image
import numpy as np

darknet_path = "/root/darknet_v2.0"
os.environ["PATH"] = darknet_path + ":" + os.environ["PATH"]

if len(glob("yolo.weights")) == 0:
    os.system("wget https://pjreddie.com/media/files/yolo.weights")


def process_video(video, output_dir):
    cmd = "darknet detector demo cfg/coco.data cfg/yolo.cfg yolo.weights {} -prefix {}".format(video, os.path.join(output_dir, "frame"))
    print(">", cmd)
    os.system(cmd)


def crop_image(image_path, tag):
    (top, bot, left, right) = (tag["top"], tag["bot"], tag["left"], tag["right"])
    print(image_path, "Top:{} Bot:{} Left:{} Right:{}".format(top, bot, left, right))

    if os.path.isfile(image_path):
        img = np.array(Image.open(image_path))
        return Image.fromarray(img[top:bot, left:right])

    return None

def target_search(output_dir, target="car"):
    target_dir = os.path.join(output_dir, target)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    with open(os.path.join(output_dir, "frame.txt")) as f:
        frame_data = [line.strip() for line in f.readlines()]

    for data in frame_data:
        info = json.loads(data)
        frame = os.path.basename(info["filename"])
        tag_list = info["tag"]
        cnt = 0
        for tag in tag_list:
            if target in tag:
                img = crop_image(os.path.join(output_dir, frame), tag)

                if img is not None:
                    file = os.path.join(target_dir, frame.replace(".jpg", "_{}_{:03d}.jpg".format(target, cnt)))
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
        target_search(output_dir)



# os.system("darknet detector demo cfg/coco.data cfg/yolo.cfg yolo.weights input/data/2017-08-16_18-07-18.avi -prefix output/frame")
