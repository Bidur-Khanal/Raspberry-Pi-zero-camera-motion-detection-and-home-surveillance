import io
import picamera
import numpy as np
from PIL import Image
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import imutils
import datetime
import memcache
from collections import deque
from threading import Thread
import socket
from get_frame import PiVideoStream


previous =None
before_previous= None
q =deque(maxlen=5)

def detect_motion(camera,vs):

    global previous
    global before_previous
    #stream = io.BytesIO()
    #camera.capture(stream, format='jpeg', resize=(320,200),use_video_port=True)
    #stream.seek(0)
    #img=Image.open(stream)
    #nparr = np.asarray(bytearray(stream.read()), dtype=np.uint8)
    #image = cv2.imdecode(nparr, cv2.CV_LOAD_IMAGE_COLOR)
    #image = cv2.imread(stream)
    image=vs.read()
    text ="Safe"
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (21, 21), 0)

    if previous is None:
        previous= gray.copy().astype("float")
    if before_previous is None:
        before_previous= gray.copy().astype("float")

    frameDelta1 = cv2.absdiff(gray, cv2.convertScaleAbs(previous))
    frameDelta2 = cv2.absdiff(cv2.convertScaleAbs(previous), cv2.convertScaleAbs(before_previous))
    frameDelta=cv2.bitwise_and(frameDelta1, frameDelta2)
    thresh = cv2.threshold(frameDelta, 10, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
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
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
            text = "Alert"

    # draw the text and timestamp on the image
    ts = datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")
    cv2.putText(image, "Room Status: {}".format(text), (10, 20),
    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    cv2.putText(image, ts, (10, image.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.35, (0, 0, 255), 1)

    before_previous= previous
    previous= gray
    q.append(image)
    timestamp = datetime.datetime.now()
    print timestamp
    
    # check to see if the room is occupied
    if text == "Alert":
        return True
    
    else:
        return False


def record_motion():
    
    with picamera.PiCamera() as camera:
            camera.resolution = (1024, 788)
            camera.framerate = 30
            vs = PiVideoStream(camera).start()
            stream = picamera.PiCameraCircularIO(camera, seconds=10)
            camera.start_recording(stream, format='h264')
            try:
                    while True:
                            #(img, value)= detect_motion(camera)
                            camera.wait_recording(0.2)
                            if detect_motion(camera,vs):
                                    print('Motion detected!')
                                    # As soon as we detect motion, split the recording to
                                    # record the frames "after" motion
                                    camera.split_recording('after.h264')
                                    # Write the 10 seconds "before" motion to disk as well
                                    stream.copy_to('before.h264', seconds=10)
                                    stream.clear()
                                    # Wait until motion is no longer detected, then split
                                    # recording back to the in-memory circular buffer
                                    while detect_motion(camera,vs):
                                            camera.wait_recording(0.2)
                                    print('Motion stopped!')
                                    camera.split_recording(stream)
                            #cv2.imshow('Security Feed',detect_motion(camera)[0])
                            #key = cv2.waitKey(1) & 0xFF
                            
            finally:
                    camera.stop_recording()
                    
def server():
        print "first thread"
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        server_socket.bind(('0.0.0.0', 6677))
        server_socket.listen(5)
        (conn, (ip,port)) = server_socket.accept()
        print "yes",ip,port
        try:
            while True:
                    if q:    
                            img=q.popleft()
                            #print img
                            #cv2.imshow("Security Feed",img)
                            #key = cv2.waitKey(1) & 0xFF
                            server.socket.send(img)
              
    
        finally:
            server_socket.close()


class ClientThread(Thread):

    def __init__(self,ip,port,sock):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        print " New thread started for "+ip+":"+str(port)

    def run(self):
        while True: 

            try:  
                data = self.sock.recv(1024)
                print('Server received', repr(data))
                print data[:5]
                if not data:
                    break
        
                if data[:5]=="10000":

                        if q:    
                            img=q.popleft()
                            self.sock.send('OK')
                            print "sent"
                            data = cv2.imencode('.jpg', img)[1].tostring()
                            self.sock.send(str(len(data)))
                            print len(data)
                            self.sock.sendall(data)
                            #self.sock.send('OK')
                            #cv2.imshow("Feed",img)
                            #key = cv2.waitKey(1) & 0xFF
                        else:
                            self.sock.send('NO')
                            print "Sent No"
                            
                '''buf= StringIO.StringIO()#create buffer
                filename='ref5.png'
                picture = Image.open(filename)
                picture=picture.resize((800,600),Image.ANTIALIAS)
                picture.save("save.jpeg")
                picture.save(buf,format='jpeg')'''
            except:
                self.sock.send("Error")
                
                



TCP_PORT = 9999
t1= Thread (target= record_motion)
t1.start()
tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
tcpsock.bind(('', TCP_PORT))
threads = []

while True:
    tcpsock.listen(5)
    print "Waiting for incoming connections..."
    (conn, (ip,port)) = tcpsock.accept()
    print 'Got connection from ', (ip,port)
    newthread = ClientThread(ip,port,conn)
    newthread.start()
    threads.append(newthread)

for t in threads:
    t.join()

