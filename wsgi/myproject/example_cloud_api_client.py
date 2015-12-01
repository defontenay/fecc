import requests
import socket
import time
import json



email = \
    {'text': "body of email",
    'attachments': 2,
    'subject': "hello world",
    'permanent': False,
    'envelope': '{"to":["william.macdonald@starleaf.com"],"from":"messenger@webex.com"}',
    'attachment-info' : '{"attachment2":{"filename":"invite.ics","name":"invite.ics","type":"application/ics"},"attachment1":{"charset":"utf-8","type":"text/calendar"}}',
    'attachment2' :'BEGIN:VCALENDAR',
}

headers = {'Content-type': 'application/json'}
session = requests.Session()
url='http://127.0.0.1:8000/email'
#url='http://fecc.starleaf.com/email'

j = json


f = open("/users/will/now.ics",'r')
email['attachment2'] = f.read()
#print json.dumps(email, sort_keys=True, indent=4, separators=(',', ': '))
r = session.post(url,data=json.dumps(email),headers=headers, verify=False)
c=r.status_code
t=r.text



print 'Response code is:', c
if c == 500:
    i = t.find('<div id="summary">')
    print t[i:i+300]
else:
    print 'Body text is:', t

