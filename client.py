'''import socket
import time
import picamera
import keyboard

#picamera.PiCamera().stop_recording()
camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 24

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
server_socket.bind(('0.0.0.0', 6677))
server_socket.listen(0)

# Accept a single connection and make a file-like object out of it
connection = server_socket.accept()[0].makefile('wb')
try:
    camera.start_recording(connection, format='h264')
    while 1:
      camera.wait_recording(1)
    
finally:
    camera.stop_recording()
    connection.close()
    server_socket.close()

import socket
import sys
import time
import picamera
import keyboard

camera = picamera.PiCamera()
camera.resolution = (640, 480)
camera.framerate = 24

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect the socket to the port on the server given by the caller
server_address = (sys.argv[1], 10000)
print >>sys.stderr, 'connecting to %s port %s' % server_address
sock.connect(server_address)

try:
    
    message = 'This is the message.  It will be repeated.'
    print >>sys.stderr, 'sending "%s"' % message
    sock.sendall(message)

    amount_received = 0
    amount_expected = len(message)
    while amount_received < amount_expected:
        data = sock.recv(16)
        amount_received += len(data)
        print >>sys.stderr, 'received "%s"' % data

finally:
    sock.close()
    camera.close()'''
    
import socket
import time
import picamera

class client_side:
    
    def __init__(self,ip,port,camera):
        self.ip = ip
        self.port = port
        print " started for "+ip+":"+str(port)
        self.client_socket = socket.socket()
        #my_server=socket.gethostbyname('SATISH-PC')
        self.client_socket.connect((self.ip,self.port))

    def Send(self,data):
            self.client_socket.sendall(data)
            '''connection = client_socket.makefile('wb')
            return connection'''


    
            
        

        
            
    

# Connect a client socket to my_server:8000 (change my_server to the
# hostname of your server)
'''client_socket = socket.socket()
my_server=socket.gethostbyname('SATISH-PC')
#my_server=socket.getservbyname('satish-pc')
print my_server
client_socket.connect(('192.168.1.69', 5005))

# Make a file-like object out of the connection
connection = client_socket.makefile('wb')
try:
    camera = picamera.PiCamera()
    camera.resolution = (640, 480)
    camera.framerate = 24
    # Start a preview and let the camera warm up for 2 seconds
    camera.start_preview()
    time.sleep(2)
    # Start recording, sending the output to the connection for 60
    # seconds, then stop
    camera.start_recording(connection, format='h264')
    camera.wait_recording(3)
    camera.stop_recording()
finally:
    connection.close()
    client_socket.close()
    camera.close()'''
