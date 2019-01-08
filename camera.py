# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import imutils
import datetime
from client import client_side as cl

# initialize the camera and grab a reference to the raw camera capture
camera = PiCamera()
height= 480
width = 640
camera.resolution = (width, height)
camera.framerate = 60
rawCapture = PiRGBArray(camera, size=(width, height))
Client= cl('192.168.1.69', 9999,camera)

# allow the camera to warmup
time.sleep(0.5)
#lastUploaded = datetime.datetime.now()
# capture frames from the camera

try:
    
    for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
            # grab the raw NumPy array representing the image, then initialize the timestamp
            image = frame.array
            image=image.flatten()
            image = image.tostring()
            print image
            Client.Send(image)
            print "one frame sent"
            break
	

	

            # clear the stream in preparation for the next frame
            rawCapture.truncate(0)
            key = cv2.waitKey(1) & 0xFF
            # if the `q` key was pressed, break from the loop
            if key == ord("q"):
                break
finally:
    camera.close()               
