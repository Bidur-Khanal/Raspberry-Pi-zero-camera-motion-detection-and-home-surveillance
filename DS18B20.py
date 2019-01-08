import os
import glob
import time

#mount temp. sensor to pi
#dtoverlay=w1-gpio-pullup,gpiopin=2  (write in boot.txt file; otherwise wont work)

        
os.system('sudo modprobe w1-gpio')
os.system('sudo modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
#automatically fetch the device folder
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

def read_temperature_raw():
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temperature():
    lines = read_temperature_raw()
    while lines[0].strip()[-3:] != 'YES' :
        time.sleep(0.01)
        lines = read_temperature_raw()

    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string)/1000
        return temp_c
                
