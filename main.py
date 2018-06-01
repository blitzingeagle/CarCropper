import os
os.environ["PATH"] = "/root/darknet_v2.0:" + os.environ["PATH"]

os.system("darknet detector demo cfg/coco.data cfg/yolo.cfg yolo.weights data/2017-08-16_18-07-18.avi -prefix results/frame")
