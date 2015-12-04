import requests
import socket
import time
import json



email = \
    {'text': "body of email",
    'attachments': "2",
    'subject': "hello world",
    'permanent': False,
    'envelope': '{"to":["william.macdonald@starleaf.com"],"from":"messenger@webex.com"}',
    'attachment-info' : '{"attachment2":{"filename":"invite.ics","name":"invite.ics","type":"application/ics"},"attachment1":{"charset":"utf-8","type":"text/calendar"}}',
}

#headers = {'Content-type': 'multipart/form-data'}
session = requests.Session()
url='http://127.0.0.1:8000/email'
#url='http://fecc.starleaf.com/email'
f = open("/users/will/nennw.ics",'rb')
files = {'attachment2':f  }
r = session.post(url,data=email,files=files, verify=False)
c=r.status_code
t=r.text



print 'Response code is:', c
if c == 500:
    i = t.find('<div id="summary">')
    print t[i:i+300]
else:
    print 'Body text is:', t

