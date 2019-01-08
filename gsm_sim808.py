import serial
import RPi.GPIO as GPIO
import os, time
import re



port =serial.Serial("/dev/ttyS0", baudrate=115200, timeout=1)

##########function to send message############
def send_message(number, message):
     print "I am here"

     port.write('AT'+'\r\n') # check the GSM+GPRS module, should return OK if working
     time.sleep(0.5)
     receive = port.read(1000)
     print receive 
 
     port.write('AT+CMGF=1'+'\r\n')# set to test mode
     time.sleep(0.5)
     receive=port.read(1000)
     print receive

 
     AT_number='AT+CMGS="{n}"'.format(n=number)
 
     port.write(AT_number+'\r\n')# the number where message is to be sent
     time.sleep(0.5)
     receive=port.read(1000)
     print receive
 
     port.write(message+'\r\n')# the text message 
     port.write('\x1A')
     time.sleep(0.5)
     receive=port.read(1000)
     print receive


#send_message("+9779843668478", "Hello")
