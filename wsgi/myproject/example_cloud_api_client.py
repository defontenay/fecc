import requests
import socket
import time
import json






web0 = \
{   "channel_id":"C0489SNJ9",
    "team_domain":"mycomp",
    "channel_name":"thischannel",
    "user_name":"Fred",
    "user_id" :"U0G0Y8D7A",
    "command":"/starleaf",
        "response_url":"http://127.0.0.0:8000/",
    "text":"m=23  u=will@starleaf.com,fred@me.org"
}


headers = {'Content-type': 'application/json'}
session = requests.Session()
url='http://127.0.0.1:8000/slack/'
#
#f = open("/users/will/new.ics",'rb')
#files = {'attachment2':f  }
#r = session.post(url,data=email,files=files, verify=False)
r = session.get(url,params=web0, headers=headers)
c=r.status_code
t=r.text
print 'Response code is:', c
if c == 500:
    i = t.find('<div id="summary">')
    print t[i:i+300]
    exit()
else:
    print 'Body text is:\n', t
