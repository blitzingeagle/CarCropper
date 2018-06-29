import os
from glob import glob

if len(glob(os.path.join(os.environ.get("DARKNET_PATH"), "weights/yolo.weights"))) == 0:
    os.system("mkdir -p {}".format(os.path.join(os.environ.get("DARKNET_PATH"), "weights")))
    os.system("wget https://pjreddie.com/media/files/yolo.weights -P {}".format(os.path.join(os.environ.get("DARKNET_PATH"), "weights")))

#if len(glob(os.path.join(os.environ.get("DARKNET_PATH"), "cfg/coco.data"))) == 0:

def process_video(video, output_dir):
    cmd = "darknet detector demo cfg/coco.data cfg/yolo.cfg weights/yolo.weights {} -avg 1 -prefix {}".format(video, os.path.join(output_dir, "result"))
    # cmd = "darknet detector demo cfg/license_plate.data cfg/license_plate.cfg license_plate_final.weights {} -avg 1 -prefix {}".format(video, os.path.join(output_dir, "frame"))
    print(">", cmd)
    os.system(cmd)

def process_videos(input_dir, frames_dir, videos=None, single=False):
    if videos is None:
        videos = sorted(glob(os.path.join(input_dir, "*.avi")))

    for video in videos:
        output_dir = os.path.splitext(video)[0].replace(input_dir, frames_dir)
        if single:
            output_dir = os.path.dirname(output_dir)

        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        if not os.path.isfile(os.path.join(output_dir, "result.txt")):
            process_video(video, output_dir)
