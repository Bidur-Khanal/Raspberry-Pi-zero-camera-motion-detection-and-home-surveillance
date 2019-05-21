import serial
import RPi.GPIO as GPIO
import os, time
import re
from threading import Thread
import logging
import requests
import json
import math
from motiondet_v2 import motiondet
import common_value as com

class GSM:
    def __init__(self):
     GPIO.setmode(GPIO.BOARD)
     self.port =serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=1)
     self.port_sms=serial.Serial("/dev/ttyAMA0", baudrate=115200, timeout=1)
     self.Continue_Poll= True
     logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-9s) %(message)s',)
     self.latitude= 0
     self.longitude= 0
     self.location= ''
    

    ##########function to send message############
    def send_message(self, number, message):

     self.port_sms.write('AT'+'\r\n') # check the GSM+GPRS module, should return OK if working
     time.sleep(0.5)
 
     self.port_sms.write('AT+CMGF=1'+'\r\n')# set to test mode
     time.sleep(0.5)
 
     self.port_sms.write('AT+CSMP= 17,167,0,4'+'\r\n')# for encoding bytes and other parameters
     time.sleep(0.5)
 
     AT_number='AT+CMGS="{n}",129'.format(n=number)
 
     self.port_sms.write(AT_number+'\r\n')# the number where message is to be sent
     time.sleep(0.5)
 
     self.port_sms.write(message+'\r\n')# the text message 
     self.port_sms.write('\x1A')
    






    ###########function to ON and OFF GPS#############
    def ONOFF_GPS( self, ONOFF):


     if ONOFF: 
      self.port.write('AT+GPS=1'+'\r\n')# open Assisted GPS
      time.sleep(0.5)
      
      self.port.write('AT+GPSRD=10'+'\r\n')# get NEMA information in 10 seconds if only GPS used instead of AGPS
      time.sleep(0.5)
     else:
      self.port.write('AT+GPS=0'+'\r\n')# open Assisted GPS
      time.sleep(0.5)
  




    ###########function to set where to store messages############
    def Set_message_storage(self):
      self.port.write('AT+CPMS="SM","SM","SM"'+'\r\n')# set the storage memory for messages// here all three set to SIM
      time.sleep(1)






 
    ###########function to read stored messages#############
    def read_stored_message(self):
     self.port.write('AT+CMGF=1'+'\r\n')# set to test mode
     time.sleep(1)

     self.port.write('AT+CMGL="ALL"'+'\r\n')# list the messages
     send=""
     for i in range(5):
      receive= self.port.read(1000) # read the response from the service provider if additional information sent
      send= send+receive
     return send 
 
 
     '''port.write('AT+CMGR=5'+'\r\n')# read a particular message with the index value
     receive= port.read(1000)
     print receive
     time.sleep(1)'''




    ###########function to send data using tcp#############
    def send_data(self):

     '''port.write('AT+CIPSHUT'+'\r\n')# SHUTDOWN IF ANY EXISTING CONNECTION
     receive= port.read(1000)
     print receive
     time.sleep(1)'''
 
     self.port.write('AT+CIPSTART="TCP","192.168.100.12",50'+'\r\n')# OPEN TCP CONNECTION
     receive= self.port.read(1000)
     print receive
     time.sleep(1)
     self.port.write('AT+CIPSEND'+'\r\n')# SEND THE DATA
     receive= self.port.read(1000)
     print receive
     time.sleep(1)
     self.port.write('DATA TO BE SENT'+'\r\n')# DATA
     receive= self.port.read(1000)
     print receive
     time.sleep(1)
     self.port.write('\x1A')
     receive= self.port.read(1000)
     print receive
     time.sleep(1)
     self.port.write('AT+CIPCLOSE'+'\r\n')# CLOSE TCP CONNECTION
     receive= self.port.read(1000)
     print receive
     time.sleep(1)
     self.port.write('AT+CIPSHUT'+'\r\n')# DISCONNECTS THE WIRELESS CONNECTION
     receive= self.port.read(1000)
     print receive
     time.sleep(1)

   

    def Reverse_Geo(self):
       
     if (self.latitude !=0) and (self.longitude!=0):
      part1 = "https://maps.googleapis.com/maps/api/geocode/json?latlng="
      part2 = str(self.latitude)+ "," +str(self.longitude)
      part3 = "&key="
      part4 = "AIzaSyDbbs8uLXb_zwnjOTfud2HVMGABCtaB6NA"
      part5 = part1+part2+part3+part4
      #print part5
      req= requests.request('GET',part5)  
      data= req.json()
      #print data
      self.location= data["results"][0][ 'formatted_address']
      '''print("address is :")
      print(data["results"][0]["address_components"][0]['long_name'])
      print(data["results"][0]["address_components"][1]['long_name'])
      print(data["results"][0]["address_components"][3]['long_name'])
      print(data["results"][0]["address_components"][4]['short_name'])
      print(data["results"][0]["address_components"][5]['long_name'])'''
      print(data["results"][0][ 'formatted_address'])
     

    

    '''***********************************************
    port.write('AT+CSDH=1'+'\r\n')# show the value in result code
    receive= port.read(100)
    print receive
    time.sleep(1)
    port.write('AT+CNMI?'+'\r\n')#new message indications
    receive= port.read(100)
    print receive
    time.sleep(1)
    **************************************************'''

    def send_location(self,number):
       if self.location: 
        message= 'Current Location: '+self.location
        self.send_message(number,message)

       else:
        message= "wait for gps to fix and try again"
        self.send_message(number,message)
        
      


        

    ############## function just to read the port##############
    def read_me(self,poll_num):
     time.sleep(1)
     receive= self.port.read(1000) # read the response from the service provider
     return receive

    

    def format_match_camera(self,value):
     r= re. compile('camera=.*')
     #s= 'Ssid=kale,psk=doctor'.lower()
     if r.match(value):
        print 'format matches'
        return 1
        
     else:
        print 'check the format!!'
        return 0

    def format_match_location(self,value):
      r= re. compile('location')
      
      if r.match(value):
        print 'format matches'
        return 1
        
      else:
        print 'check the format!!'
        return 0



        
    def start_poll(self):
      self.set_to_textmode()
      # start the thread to poll the sms
      th=Thread(target=self.poll, args=())
      th.start()
      return self  

    def stop_poll(self):
      #stop the thread for polling
      self.Continue_Poll= False  
      


    def set_to_textmode(self):
      self.port.write('AT+CMGF=1'+'\r\n')# set to test mode
      time.sleep(0.5)

    def motiondetection(self):
       logging.debug("thread")
       Mo= motiondet()
       Mo.cam()
        
           
        
         




    def start_motion(self):
      mot=Thread(target=self.motiondetection, args=())
      mot.start()
      return

        
    
    #######continuosly read sms commands or gps coordinate ##########
    def poll(self):
  
     while (self.Continue_Poll):
      read= self.read_me(self.port)   
      print read
      #logging.debug("thread")
      read1= read.split('\n')

      
      for i in range(len(read1)):

       #reads the sms if available in port and sets the camera parameter   
       if read1[i].lower().startswith('camera'):
         if self.format_match_camera(read1[i].lower()): 
          read2=read1[i].split(',')
          read_camera=  read2[0].split('=')
          camera_mode= read_camera[1].lower()
          r= re. compile('motion')
          r1=re.compile('stop')
          if r.match(camera_mode):
            if (not com.motion_start):
              com.motion_start= True
              print com.motion_start
              #print com.get_value()
              self.start_motion()
          if r1.match(camera_mode):
              com.motion_start= False

       #reads the sms; if location in sms, sends location to the give number
       if read1[i].lower().startswith('location'):
        if self.format_match_location(read1[i].lower()):
            previous_line= read1[i-1]
            if previous_line.startswith('+CMT'):
                read_split=previous_line.split(',')
                has_number= read_split[0].split(':')
                number= has_number[1]
                print number
                self.send_location(eval(number))
                
                
          
           
              
       #reads the GPS NMEA and sets the latitude, longitude and time  
       if read1[i].startswith('+GPSRD'):
        All_Data=read1[i].split(',')
        if(int(All_Data[6])==1):
         lat = float (All_Data[2])/100
         lat_whole= math.floor(lat)
         lat_frac= (lat-lat_whole)/60*100
         degree_lat=lat_whole+lat_frac
         self.latitude=degree_lat
         
         lng = float (All_Data[4])/100
         lng_whole= math.floor(lng)
         lng_frac=(lng-lng_whole)/60*100
         degree_lng=lng_whole+lng_frac
         self.longitude=degree_lng

        

       

    


    
                
               
    
        

    
    
    
