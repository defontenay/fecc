import requests
import socket
import time

session = requests.Session()
url='http://127.0.0.1:8000/poll'
#url='http://fecc.starleaf.com/poll'
print "getting ",url
while True:
    response = session.get(url)
    body = response.text
    if body != ".":
        print body
    time.sleep(1)



#host = 'fecc-codian.rhcloud.com'
#port = 50007
#size = 1024
#s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#print "coinnecting to ", host
#s.connect((host,port))
#print "connected"
#try:
#    while 1:
#        print "listening"
#        data = s.recv(size)
#        print 'Received:', data
#except:
#    s.close()



