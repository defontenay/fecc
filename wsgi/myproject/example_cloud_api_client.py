import requests
import socket

#session = requests.Session()
#url='http://127.0.0.1:8000/poll'
#url='http://fecc.starleaf.com/poll'
#print "getting ",url
#while True:
#    response = session.get(url)
#    body = response.text
#    print body



host = '127.0.0.1'
port = 50007
size = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((host,port))
try:
    while 1:
        data = s.recv(size)
        print 'Received:', data
except:
    s.close()



