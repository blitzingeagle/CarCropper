import os
os.environ["PATH"] = "/root/darknet_v2.0/:" + os.environ["PATH"]

os.system("darknet detector")
