import cv2
from base_camera import BaseCamera
from darkflow.net.build import TFNet
from pykinect2 import PyKinectV2
from pykinect2.PyKinectV2 import *
from pykinect2 import PyKinectRuntime
import numpy as np
import time
import tensorflow as tf


config = tf.ConfigProto(log_device_placement=True)
config.gpu_options.allow_growth = True
with tf.Session(config=config) as sess:
    options = {
            'model': 'cfg/yolov2-tiny-voc.cfg',
            'load': 'bin/yolov2-tiny-voc.weights',
            'threshold': 0.2,
            'gpu': 0.5
                    }
    tfnet = TFNet(options)

colors = [tuple(255 * np.random.rand(3)) for _ in range(10)]



class Camera(BaseCamera):

    def frames():
        kinect = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Color)
        kinectD = PyKinectRuntime.PyKinectRuntime(PyKinectV2.FrameSourceTypes_Depth)
        while True:
            stime = time.time()
            if kinect.has_new_color_frame():
                frame = kinect.get_last_color_frame()
                frame = np.reshape(frame, (1080, 1920, 4))
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
                frame = cv2.resize(frame, (0, 0), fx=.5, fy=.5)
                #frameC = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)

                frameD = kinectD.get_last_depth_frame()
                frameDepth = kinectD._depth_frame_data
                depthxy = kinectD._depth_frame_data
                depthxy = np.reshape(depthxy, (424, 512))
                frameD = frameD.astype(np.uint8)
                frameD = np.reshape(frameD,(424, 512))
                frameD = cv2.cvtColor(frameD, cv2.COLOR_GRAY2BGR)


                results = tfnet.return_predict(frame)
                for color, result in zip(colors, results):
                    tl = (result['topleft']['x'], result['topleft']['y'])
                    br = (result['bottomright']['x'], result['bottomright']['y'])
                    x_Center = int((((result['topleft']['x']) + (result['bottomright']['x']))/2))
                    y_Center = int((((result['topleft']['y']) + (result['bottomright']['y']))/2))
                    Center = (int(x_Center /2), int(y_Center * .8))
                    #Center = (int((x_Center / 8) * 2.5), int(y_Center * .45))
                    CenterC = int(x_Center), int(y_Center)
                    Pixel = depthxy[int(y_Center * .8)]
                    #Pixel_Depth = frameDepth[((int(y_Center * .8) *  512) + int(x_Center /2))]
                    #Pixel_Depth = Pixel[int((x_Center / 8) * 2.5)]
                    Pixel_Depth = Pixel[int(x_Center / 2)]
                    label = result['label']
                    confidence = result['confidence']
                    text = '{}:{:.0f}%'.format(label,confidence * 100)
                    textD = 'Depth{}mm'.format(Pixel_Depth)
                    frame = cv2.rectangle(frame, tl, br, color, 5)
                    frameD = cv2.circle(frameD, Center, 10, color, -1)
                    frame = cv2.putText(frame, text, tl, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)
                    frame = cv2.putText(frame, textD, CenterC, cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)

                cv2.imshow('frame', frame)
                cv2.imshow('frameD', frameD)
                yield cv2.imencode('.jpg', frame)[1].tobytes()
                #print([result][0:1])
                frame = None
                #print('FPS {:.1f}'.format(1 / (time.time() - stime)))
            if cv2.waitKey(1) & 0xFF == ord('q'):
               break


    cv2.destroyAllWindows()
