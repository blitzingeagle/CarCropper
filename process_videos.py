import os
from glob import glob

darknet_path = "/root/darknet_v2.0"
os.environ["PATH"] = darknet_path + ":" + os.environ["PATH"]

if len(glob("yolo.weights")) == 0:
    os.system("wget https://pjreddie.com/media/files/yolo.weights")


def process_video(video, output_dir):
    cmd = "darknet detector demo cfg/coco.data cfg/yolo.cfg yolo.weights {} -avg 1 -prefix {}".format(video, os.path.join(output_dir, "frame"))
    print(">", cmd)
    os.system(cmd)

def process_videos():
    input_dirs = sorted(glob("input/*"))
    for input_dir in input_dirs:
        videos = sorted(glob(os.path.join(input_dir, "*.avi")))

        for video in videos:
            output_dir = os.path.splitext(video)[0].replace("input", "frames")
            if not os.path.exists(output_dir):
                os.makedirs(output_dir)

            if not os.path.isfile(os.path.join(output_dir, "frame.txt")):
                process_video(video, output_dir)
