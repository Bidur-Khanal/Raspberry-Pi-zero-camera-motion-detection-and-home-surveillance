import threading
import time
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import cv2
import imutils
import datetime
import logging
#import common_value as com


class motiondet:

 def __init__(self):
     print "Please enter the number of grids you want (row x column)"
     self.grid_row= int(raw_input("Row: "))
     self.grid_column= int(raw_input("Column: "))
     self.grid_size= self.grid_row*self.grid_column
     self.avg=[None]*self.grid_size
     self.previous =[None]*self.grid_size
     self.before_previous=[None]*self.grid_size
     self.face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
     self.eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
     



       
 #########draw the grid boxes########
 def draw_grid(self,image,height,width, row, column):
       for k in range( 0,width, row):
        cv2.line(image,(k,0),(k,height),(255,255,255),2)
       for k in range (0,height,column): 
        cv2.line(image,  (0,k),(width,k),(255,255,255),2)


 ##########take a portion of image as a grid and find motion detection in that grid##########
 def process_eachgrid(self,image,template_x, template_y,grid, width_size, height_size):
    
    image1= image[template_y:template_y+height_size,template_x:template_x+width_size]
    timestamp = datetime.datetime.now() #get the current time
    text = "Safe"
    gray0 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray0, (21, 21), 0)


    # if the average frame is None, initialize it
        
    if self.avg[grid] is None :
		print("Initializing the background")
		im = gray.copy().astype("float")
		self.avg.insert(grid,im)

    if self.previous[grid] is None :
                im = gray.copy().astype("float")
	        self.previous[grid]=im

    if self.before_previous[grid] is None :
                im = gray.copy().astype("float")
	        self.before_previous[grid]=im
	        
    frameDelta1 = cv2.absdiff(gray, cv2.convertScaleAbs(self.previous[grid]))
    frameDelta2 = cv2.absdiff(cv2.convertScaleAbs(self.previous[grid]), cv2.convertScaleAbs(self.before_previous[grid]))
    frameDelta=cv2.bitwise_and(frameDelta1, frameDelta2)
    faces = self.face_cascade.detectMultiScale(gray0, 1.3, 5)
    for (x,y,w,h) in faces:
      cv2.rectangle(image,(x,y),(x+w,y+h),(255,255,0),2)
      roi_gray = gray[y:y+h, x:x+w]
      print "faces"
      eyes = self.eye_cascade.detectMultiScale(roi_gray,1.3,5)
      for (ex,ey,ew,eh) in eyes:
        cv2.rectangle(image,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
        print "eyes"

	        

           

    		

          	
    # accumulate the weighted average between the current frame and
    # previous frames, then compute the difference between the current
    # frame and running average
    #cv2.accumulateWeighted(gray, avg[grid], 0.2)
    #frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(avg[grid]))

    # threshold the delta image, dilate the thresholded image to fill
    # in holes, then find contours on thresholded image
    
    thresh = cv2.threshold(frameDelta, 5, 255, cv2.THRESH_BINARY)[1]
    thresh = cv2.dilate(thresh, None, iterations=2)
    cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
		cv2.CHAIN_APPROX_SIMPLE)
    cnts = cnts[0] if imutils.is_cv2() else cnts[1]
   
    # loop over the contours
    for c in cnts:
		# if the contour is too small, ignore it
		if cv2.contourArea(c) < 100:
			continue

		# compute the bounding box for the contour, draw it on the frame,
		# and update the text
		(x, y, w, h) = cv2.boundingRect(c)
		cv2.rectangle(image, (template_x+x, template_y+y), (template_x+x + w, template_y+y + h), (0, 255, 0), 2)
		text = "Alert"
    # update the previous and before_previous frames
    self.before_previous[grid]= self.previous[grid]
    self.previous[grid]= gray

	
    # check to see if the room is occupied
    if text == "Alert":
		print "Motion Detected in GRID",grid
		
    # draw the text on the image
    cv2.putText(image, "Room Status: {}".format(text), (template_x+10, template_y+20),
		cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

   
			

	

    
    
    
	
        
 def cam(self):
  # initialize the camera and grab a reference to the raw camera capture
  camera = PiCamera()
  height= 500
  width = 500
  camera.resolution = (width, height)
  camera.framerate = 60
  #camera.color_effects=(128,128)
  camera.iso=500
  #camera.image_effect='denoise'
  #camera.exposure_mode = 'night'
  rawCapture = PiRGBArray(camera, size=(width, height))

  # allow the camera to warmup
  time.sleep(0.5)
  
  logging.basicConfig(level=logging.DEBUG,
                       format='[%(levelname)s] (%(threadName)-9s) %(message)s',)
  
  try:
   for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    # grab the raw NumPy array representing the image
    image = frame.array
    logging.debug("Thread")
    #print image
    #print cv2.mean(image)
    template_y=0
    template_x=0
    grid=0
    width_size= int(width/self.grid_column)
    height_size= int(height/self.grid_row)
    for i in range (self.grid_row):
      template_x=0
      for j in range(self.grid_column):     
        #t = threading.Thread(target=process_eachgrid, args=(image,template_x,template_y,grid,width_size,height_size))
        #t.start()
        #t.join()
        self.process_eachgrid(image,template_x,template_y,grid,width_size,height_size)
        template_x= template_x+width_size
        grid= grid+1
      template_y= template_y+height_size
    self.draw_grid(image,height,width,width_size,height_size)
    #print com.motion_start
    # clear the stream in preparation for the next frame
    rawCapture.truncate(0)
    # show the image
    cv2.imshow("Security Feed", image)
    key = cv2.waitKey(1) & 0xFF

    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
	break
    #if not com.motion_start:
        #break

  finally:
    #com.motion_start= False
    cv2.destroyWindow("Security Feed")
    
    
