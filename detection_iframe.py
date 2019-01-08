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
from collections import deque
from threading import Thread
import socket
import csv
import sqlite3
import json
import control_output as cl
import DS18B20 as temp



#loads the file from the 
def json_load():
      with open("Data/configuration.json", "r") as jsonFile:
             data = json.load(jsonFile)
      return data
             

      
      


def load_configuration():
      global Threshold
      conn = sqlite3.connect('Data/configuration.sqlite')
      print "Opened database successfully";

      query = conn.execute("SELECT DEFAULT_SENSITIVITY from Camera where DEVICE='camera1'")
      Threshold =query
      print Threshold
      
      

      print "Operation done successfully";
      conn.close()
      return Threshold



#### write the temperature log to a file
def write_temperature(temperature):
        with open('Data/Temperature_log.csv', 'a') as f:
             current_time=datetime.datetime.now()
             ts = current_time.strftime("%A-%d-%B-%Y-%I-%M-%S%p")
             writer = csv.writer(f)
             writer.writerow([temperature,ts])

#log reads the temperature continuously and logs every 10 minutes
def temperature_unit():
      counter =0
      global config
      output_status=0
      while True:
            counter =counter +1
            temperature_value=temp.read_temperature()
            print "Temperature" ,temperature_value
            status=config["Devices_Settings"]["Temperature"][0]["Status"]
            Temp_Threshold=config["Devices_Settings"]["Temperature"][0]["Threshold_Value"]
            
            
            

            if counter >10:
                  counter=0
                  print "temperature log"
                  write_temperature(temperature_value)

            if temperature_value > Temp_Threshold and output_status ==0 and status==1:
                  #call set alarm
                  alarm_output= config["Triggers"][1]["Alarm_Output"]
                  print alarm_output
                  #triggers(alarm_output)s
                  cl.Output(alarm_output,"Temperature 1",config,0)
                  output_status=1
            if temperature_value < Temp_Threshold:
                  output_status =0
                  
                  
                  
            
      



####read the camera sensitivity from the file
def get_Threshold():
      global Threshold        
      with open('Data/Threshold.csv', 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
             Threshold=float(row[0])
             return Threshold
            
def all_query(qur):
      try:
            conn = sqlite3.connect('Data/configuration.sqlite')
            print "Opened database successfully";

            query = conn.execute(qur)
            return query
      except IOError as e:
            return "I/O error({0}): {1}".format(e.errno, e.strerror)
      

            


#### write the camera sensitivity to the file
def write_Threshold(threshold):
        with open('Data/Threshold.csv', 'wb') as f:
             writer = csv.writer(f)
             writer.writerow([threshold])

             
#### write the motion detected time to a log file
def write_motion(time):
        with open('Data/Motion_log.csv', 'a') as f:
             writer = csv.writer(f)
             writer.writerow([time])
             

def detect_motion(camera):

    global previous
    global before_previous
    
    Threshold = config["Devices_Settings"]["Camera"][0]["Current_Sensitivity"]
    stream = io.BytesIO()
    camera.capture(stream, format='jpeg', resize=(350,250),use_video_port=True)
    stream.seek(0)
    #img=Image.open(stream)
    nparr = np.asarray(bytearray(stream.read()), dtype=np.uint8)
    image = cv2.imdecode(nparr, cv2.CV_LOAD_IMAGE_COLOR)
    text ="Safe"
    if config["Devices_Settings"]["Camera"][0]["Status"]==1:
          gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
          gray = cv2.GaussianBlur(gray, (21, 21), 0)

          if previous is None:
              previous= gray.copy().astype("float")
          if before_previous is None:
              before_previous= gray.copy().astype("float")

          frameDelta1 = cv2.absdiff(gray, cv2.convertScaleAbs(previous))
          frameDelta2 = cv2.absdiff(cv2.convertScaleAbs(previous), cv2.convertScaleAbs(before_previous))
          frameDelta=cv2.bitwise_and(frameDelta1, frameDelta2)
          thresh = cv2.threshold(frameDelta, Threshold, 255, cv2.THRESH_BINARY)[1]
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
          before_previous= previous
          previous= gray

    # draw the text and timestamp on the image
    ts = datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p")
    cv2.putText(image, "Room Status: {}".format(text), (10, 20),
    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    cv2.putText(image, ts, (10, image.shape[0] - 10), cv2.FONT_HERSHEY_SIMPLEX,
                        0.35, (0, 0, 255), 1)

    
    q.append(image)
    timestamp = datetime.datetime.now()
    print timestamp
    
    # check to see if the room is occupied
    if text == "Alert":
        count=0 
        alarm_output= config["Triggers"][0]["Alarm_Output"]
        print alarm_output
        #triggers(alarm_output)
        cl.Output(alarm_output,"Camera1",config,count)
        count= count+1
        if count <60:
              count =0
        return True
    
    else:
        return False


def record_motion():
    
    with picamera.PiCamera() as camera:
            camera.resolution = (1500, 800)
            camera.framerate = 30
            stream = picamera.PiCameraCircularIO(camera, seconds=10)
            camera.start_recording(stream, format='h264')
            try:
                    while True:
                            #(img, value)= detect_motion(camera)
                            camera.wait_recording(0.2)
                            if detect_motion(camera):
                                    print('Motion detected!')
                                    # As soon as we detect motion, split the recording to
                                    # record the frames "after" motion
                                    timestamp=datetime.datetime.now()
                                    ts = timestamp.strftime("%A-%d-%B-%Y-%I-%M-%S%p")
                                    print ts
                                    camera.split_recording('Video_Data/after-{t}.h264'.format(t=ts))
                                    # Write the 10 seconds "before" motion to disk as well
                                    stream.copy_to('Video_Data/before-{t}.h264'.format(t=ts), seconds=10)
                                    stream.clear()
                                    write_motion(ts)
                                    # Wait until motion is no longer detected, then split
                                    # recording back to the in-memory circular buffer
                                    while detect_motion(camera):
                                            camera.wait_recording(0.2)
                                    print('Motion stopped!')
                                    camera.split_recording(stream)
                            #cv2.imshow('Security Feed',detect_motion(camera)[0])
                            #key = cv2.waitKey(1) & 0xFF
            except IOError as e:
                  self.sock.send ("I/O error({0}): {1}".format(e.errno, e.strerror))

                             
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
        global Threshold
        global config
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
                            print 'sent'
                            data = cv2.imencode('.jpg', img)[1].tostring()
                            size=len(data)
                            digits=str(size).zfill(8)
                            #print digits
                            self.sock.send(str(digits))
                            self.sock.sendall(data)
                            #cv2.imshow("Feed",img)
                            #key = cv2.waitKey(1) & 0xFF
                        else:
                            self.sock.send('NO')
                            #print 'sent No'
                if data[:5]=="10001":
                        val= int(get_Threshold()-5)
                        self.sock.send(str(val))
                        print val
                if data[:5]=="10002":
                        value=data[5:6]
                        print value
                        Threshold =5+int(value)
                        write_Threshold(Threshold)
                        print Threshold
                if data[:5]=="10003":
                        query= data[5:]
                        back= all_query(query)
                        self.sock.send(str(back))

                if data[:5]=="10004":
                        '''with open('Data/Motion_log.csv', 'rb') as f:
                              print "here"
                              reader = csv.reader(f)
                              for row in reader:
                                     self.sock.send(str(row))
                                     print row'''
                        f = open('Data/Motion_log.csv', 'rb')
                        File = f. read()
                        size=len(File)
                        digits=str(size).zfill(8)
                        print digits
                        self.sock.send(str(digits))
                        self.sock.send(str(File))
                        #self.sock.send(File.tostring())
                        
                        
                        print "Sending Complete"

                if data[:5]=="10005":
                       filename=data[5:]
                       print filename
                       directory= "Video_Data/"
                       filename_before_detection= directory+'before-'+filename+'.h264'
                       filename_after_detection= directory+'after-'+filename+'.h264'
                       print filename_before_detection
                       print filename_after_detection
                       f1 = open(filename_before_detection, 'rb')
                       f2= open(filename_after_detection,'rb')
                       File1 = f1.read()
                       size1=len(File1)
                       digits1=str(size1).zfill(8)
                       File2 = f2.read()
                       size2=len(File2)
                       digits2=str(size2).zfill(8)
                       print digits1
                       print digits2
                       self.sock.send(str(digits1))
                       self.sock.send(str(File1))
                       self.sock.send(str(digits2))
                       self.sock.send(str(File2))
                        
                       print "Sending Complete"

                if data[:5]=="10006":
                       f = open('Data/configuration.json', 'rb')
                       File = f. read()
                       size=len(File)
                       digits=str(size).zfill(8)
                       print digits
                       self.sock.send(str(digits))
                       self.sock.send(str(File))
                       #self.sock.send(File.tostring())
                if data[:5]=="10007":
                      try:
                       File= data[5:]
                       with open('Data/configuration.json', 'wb') as f:
                             f.write(File)
                       config = json_load()
                       
                       self.sock.send("Written to file")
                      except:
                       self.sock.send("Could not write to the file")
                       
                        
                        
                      

                            
                '''buf= StringIO.StringIO()#create buffer
                filename='ref5.png'
                picture = Image.open(filename)
                picture=picture.resize((800,600),Image.ANTIALIAS)
                picture.save("save.jpeg")
                picture.save(buf,format='jpeg')'''

            except IOError as e:
                  self.sock.send ("I/O error({0}): {1}".format(e.errno, e.strerror))

                
                

previous =None
before_previous= None
q =deque(maxlen=5)
#Threshold = get_Threshold()
TCP_PORT = 9999
config = json_load()
t2= Thread (target= temperature_unit)
t2.start()
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

