import socket
from threading import Thread
from SocketServer import ThreadingMixIn
from PIL import Image
import StringIO
import picamera as bf
import buffering
import cv2
import time
import StringIO
import memcache



class SplitFrames(object):
    
    def __init__(self, connection):
        self.connection = connection
        self.stream = io.BytesIO()
        self.count = 0

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # Start of new frame; send the old one's length
            # then the data
            size = self.stream.tell()
            if size > 0:
                self.connection.write(struct.pack('<L', size))
                self.connection.flush()
                self.stream.seek(0)
                self.connection.write(self.stream.read(size))
                self.count += 1
                self.stream.seek(0)
        self.stream.write(buf)

class ClientThread(Thread):

    def __init__(self,ip,port,sock):
        Thread.__init__(self)
        self.ip = ip
        self.port = port
        self.sock = sock
        print " New thread started for "+ip+":"+str(port)
        #self.shared= memcache.Client(['127.0.0.1:11211'],debug=0)
        

    def run(self):


        data = self.sock.recv(1024)
        print('Server received', repr(data))
        print data[:5]
        
        if data[:5]=="10001":
            try:
                 while True:
                     time.sleep(1)
                     '''camera = picamera.PiCamera()
                     camera.resolution = (640, 480)
                     camera.framerate = 24
                     print "i am 1"
                     camera.start_recording(self.connection, format='h264')
                     print "here"
                     while 1:
                     self.camera.wait_recording(1)
                 
                 
                     self.sock.send('OK')
                     sent=self.sock.send(buf.getvalue())
                     self.sock.send('OK')
                     print sent'''
                     print "herer"
                     '''buf= StringIO.StringIO()
                     image= cv2.imread('temp.jpg')
                     image.save(buf,format='jpg')'''
                     #image= self.shared.get('Frame')
                     #cv2.imshow("Security Feed", image)
                     
                 
            except:
                 self.sock.send("Error")
            '''finally:
                 camera.stop_recording()
                 camera.close()'''
            
       
class server_side():

    def __init__(self):
        
        TCP_PORT = 9999
        self.tcpsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcpsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.tcpsock.bind(('', TCP_PORT))
        self.threads = []

    def run_server(self):

        while True:
            self.tcpsock.listen(5)
            print "Waiting for incoming connections..."
            (conn, (ip,port)) = self.tcpsock.accept()
            print 'Got connection from ', (ip,port)
            newthread = ClientThread(ip,port,conn)
            newthread.start()
            self.threads.append(newthread)

        for t in threads:
            t.join()



