import requests
import socket
import time
import json
import warnings




headers = {'Content-type': 'application/json'}
warnings.filterwarnings("ignore")
url='http://127.0.0.1:8000/zapcal/william.macdonald@starleaf.com'
#url='http://fecc.starleaf.com/zapcal/will@starleaf.com'
web = { \
    "end__dateTime":'2016-09-17T15:30:00Z', \
    "Subject":'Wills New Meeting',\
    "start__dateTime":'2016-09-17T02:00:00-07:00',\
    "iCalUId":'willsuniqusssssd2',\
    "IsCancelled":'True',\
    "StartTimeZone":'Pacific',\
    "description":' <font size="4"><span style="font-size:16pt"><a href="https://meet.lync.com/starleaf1/william.macdonald/3XZN1VDW" target="_blank">Join online meeting </a>'   }


session = requests.Session()

print "calling...",url

r = session.post(url,data=web, verify=False)
c=r.status_code
t=r.text
print 'Response code is:', c
if c == 500:
    i = t.find('<div id="summary">')
    print t[i:i+300]
    exit()
else:
    print 'Body text is:\n', t
