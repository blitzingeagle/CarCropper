FROM blitzingeagle/darknet:v2.0

RUN apt-get update && apt-get install -y python3-dev python3-pip virtualenv

RUN cd /root/ && git clone https://github.com/blitzingeagle/CropYOLO.git && \
    cd CropYOLO && pip3 install -r requirements.txt && \
    mkdir weights && wget https://pjreddie.com/media/files/yolov2.weights -P weights
