import RPi.GPIO as GPIO
from threading import Thread
import time
import gsm_sim808 as ms



GPIO.setmode(GPIO.BOARD)
GPIO.setup(29, GPIO.OUT)
GPIO.setup(31, GPIO.OUT)
GPIO.setup(33, GPIO.OUT)
GPIO.setup(35, GPIO.OUT)
GPIO.setup(37, GPIO.OUT)
GPIO.output(29, GPIO.LOW)
GPIO.output(31, GPIO.LOW)
GPIO.output(33, GPIO.LOW)
GPIO.output(35, GPIO.LOW)
GPIO.output(37, GPIO.LOW)

def Output(alarms,input_trigger,config,count):
    for function in alarms:
        t= Thread (target= eval(function),args=(input_trigger,config,count))
        t.start()

def Output1(input_trigger,config,count):
    GPIO.output(29, GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(29, GPIO.LOW)

def Output2(input_trigger,config,count):
    GPIO.output(31,GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(31, GPIO.LOW)

def Output3(input_trigget,config,count):
    GPIO.output(33,GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(33, GPIO.LOW)

def Output4(input_trigger,config,count):
    GPIO.output(35,GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(35, GPIO.LOW)

def Output5(input_trigger,config,count):
    GPIO.output(37,GPIO.HIGH)
    time.sleep(0.2)
    GPIO.output(37, GPIO.LOW)

def Output6(input_trigger,config,count):
    message= "Alert from Unit: " +input_trigger
    numbers= config["Phone_Book"]
    for num in numbers:
        if count==0:
            number=str(num)
            print message,number
            #ms.send_message(num, message)
    
    
    
    
        
        


   
    
    
