import requests
import socket
import time
import json



email = \
    {'text': "body of email",
    'attachments': 3,
    'subject': "hello world",
    'permanent': False,
    'envelope': {"to":["will@test.cloud.sl"],"from":"messenger@webex.com"},
    'attachment-info' : {"attachment2":{"filename":"invite.ics","name":"invite.ics","type":"application/ics"},"attachment1":{"charset":"utf-8","type":"text/calendar"}},
    'attachment2' :"fake ics lots of data ics more data etc",
}

headers = {'Content-type': 'application/json'}
session = requests.Session()
url='http://127.0.0.1:8000/email'
#url='http://fecc.starleaf.com/email'
print json.dumps(email, sort_keys=True, indent=4, separators=(',', ': '))
r = session.post(url,data=json.dumps(email),headers=headers, verify=False)
print 'Response code is:', r.status_code
print 'Body text is:', r.text

