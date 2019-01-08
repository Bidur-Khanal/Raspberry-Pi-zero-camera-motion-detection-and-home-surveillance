# import the necessary packages
from picamera.array import PiRGBArray
from picamera import PiCamera
import io
import socket
import StringIO
import time
import cv2
import imutils
import datetime
from collections import deque
import memcache
from threading import Thread





def motion():
        print "second thread"
        # initialize the camera and grab a reference to the raw camera capture
        camera = PiCamera()
        height= 480
        width = 640
        camera.resolution = (width, height)
        camera.framerate = 60
        #camera.color_effects=(128,128)
        #camera.iso=500
        #camera.image_effect='denoise'
        rawCapture = PiRGBArray(camera, size=(width, height))
        #shared= memcache.Client(['127.0.0.1:11211'],debug=0)


        #stream the video to this port using the socket tcp/ip conncetion 

        # allow the camera to warmup
        time.sleep(0.5)
        lastUploaded = datetime.datetime.now()
        avg = None
        previous =None
        before_previous= None
        # capture frames from the camera
        for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
                # grab the raw NumPy array representing the image, then initialize the timestamp
                image = frame.array

                timestamp = datetime.datetime.now()
                print timestamp
                text = "Safe"
                #image= imutils.resize(image, width=500)
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                gray = cv2.GaussianBlur(gray, (21, 21), 0)
                #edge= cv2.Canny(gray,50,150)
                
                if previous is None:
                        previous= gray.copy().astype("float")
                if before_previous is None:
                        before_previous= gray.copy().astype("float")


                
                # accumulate the weighted average between the current frame and
                # previous frames, then compute the difference between the current
                # frame and running average
                #cv2.accumulateWeighted(edged, avg, 0.5)
                frameDelta1 = cv2.absdiff(gray, cv2.convertScaleAbs(previous))
                frameDelta2 = cv2.absdiff(cv2.convertScaleAbs(previous), cv2.convertScaleAbs(before_previous))
                frameDelta=cv2.bitwise_and(frameDelta1, frameDelta2)
                #edged = cv2. Canny(frameDelta,50,150)

                # threshold the delta image, dilate the thresholded image to fill
                # in holes, then find contours on thresholded image
                thresh = cv2.threshold(frameDelta, 10, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)
                '''thresh1 = cv2.threshold(frameDelta1, 10, 255, cv2.THRESH_BINARY)[1]
                thresh1 = cv2.dilate(thresh1, None, iterations=2)
                thresh2 = cv2.threshold(frameDelta2, 10, 255, cv2.THRESH_BINARY)[1]
                thresh2 = cv2.dilate(thresh2, None, iterations=2)'''
                cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                        cv2.CHAIN_APPROX_SIMPLE)
                cnts = cnts[0] if imutils.is_cv2() else cnts[1]

                # loop over the contours
                for c in cnts:
                        # if the contour is too small, ignore it
                        if cv2.contourArea(c) < 250:
                                continue

                        # compute the bounding box for the contour, draw it on the frame,
                        # and update the text
                        '''(x, y, w, h) = cv2.boundingRect(c)
                        cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)'''
                        text = "Alert"

                # draw the text and timestamp on the image
                ts = timestamp.strftime("%A %d %B %Y %I:%M:%S%p")
                cv2.putText(image, "Room Status: {}".format(text), (10, 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
                cv2.putText(image, ts, (10, image.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.35, (0, 0, 255), 1)

                # check to see if the room is occupied
                if text == "Alert":
                        print "motion detected"
                q.append(image)
                #shared.set('Frame',"one")
                # show the image
                #bf.q.appendleft(image)
                #cv2.imwrite('temp.jpg',image)
                #cv2.imshow("Security Feed", image)
                
                '''cv2.imshow("Frame Delta1 Thresh", thresh1)
                cv2.imshow("Frame Delta2 Thresh",thresh2)
                cv2.imshow("Thresh", thresh)
                cv2.imshow("Frame Delta1", frameDelta1)
                cv2.imshow("Frame Delta2", frameDelta1)
                cv2.imshow("Frame Delta", frameDelta)'''
                key = cv2.waitKey(1) & 0xFF
                before_previous= previous
                previous= gray

                # clear the stream in preparation for the next frame
                rawCapture.truncate(0)

                # if the `q` key was pressed, break from the loop
                if key == ord("q"):
                        break


def server():
        print "first thread"
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        server_socket.bind(('0.0.0.0', 6677))
        server_socket.listen(5)
        (conn, (ip,port)) = server_socket.accept()
        print "yes",ip,port
        try:

            while 1:
                    if q:
                            img=q.popleft()
                            cv2.imshow("Security Feed",img)
                            #server.socket.send(img)
              
    
        finally:
            server_socket.close()


q= deque(maxlen=3)
t1= Thread (target= server)
t2= Thread (target= motion)
t2.start()
t1.start()


        
