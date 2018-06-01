import os
from glob import glob

darknet_path = "/root/darknet_v2.0"
os.environ["PATH"] = darknet_path + ":" + os.environ["PATH"]

if len(glob("yolo.weights")) == 0:
    os.system("wget https://pjreddie.com/media/files/yolo.weights")


def process_video(video, output_dir):
    cmd = "darknety detector demo cfg/coco.data cfg/yolo.cfg yolo.weights {} -prefix {}".format(video, os.path.join(output_dir, "frame"))
    print(">", cmd)
    os.system(cmd)


def crop_images(output_dir, tag="car"):
    target_dir = os.path.join(output_dir, tag)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    with open(os.path.join(output_dir, "frame.txt")) as f:
        content = f.readlines()


input_dirs = glob("input/*")
for input_dir in input_dirs:
    videos = glob(os.path.join(input_dir, "*.avi"))

    for video in videos:
        output_dir = os.path.splitext(video)[0].replace("input", "output")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        process_video(video, output_dir)
        crop_images(output_dir)



# os.system("darknet detector demo cfg/coco.data cfg/yolo.cfg yolo.weights input/data/2017-08-16_18-07-18.avi -prefix output/frame")
